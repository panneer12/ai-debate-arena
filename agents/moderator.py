"""Moderator agent for AI Debate Arena."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from agents.base_agent import BaseDebateAgent
from protocols.debate_protocol import DebatePhase, DebateProtocol
from protocols.message_format import DebateMessage, MessageType

logger = logging.getLogger(__name__)


class ModeratorAgent(BaseDebateAgent):
    """
    Moderator agent that orchestrates the debate flow.
    """

    def __init__(self):
        super().__init__(name="Moderator", role="Moderator")
        self.protocol = DebateProtocol()
        self.current_phase = DebatePhase.SETUP
        self.participants: List[BaseDebateAgent] = []
        self.topic = ""
        self.turn_order: List[BaseDebateAgent] = []
        self.current_turn_index = 0
        self.history: List[DebateMessage] = []

    async def start_debate(
        self,
        topic: str,
        debaters: List[BaseDebateAgent],
        fact_checker: Optional[BaseDebateAgent] = None,
        devils_advocate: Optional[BaseDebateAgent] = None,
        synthesizer: Optional[BaseDebateAgent] = None,
    ) -> Dict[str, Any]:
        """
        Start and manage the full debate lifecycle.
        """
        self.topic = topic
        self.participants = debaters
        self.fact_checker = fact_checker
        self.devils_advocate = devils_advocate
        self.synthesizer = synthesizer

        logger.info(f"Starting debate on topic: {self.topic}")

        # Announce start
        await self._broadcast(f"Welcome to the AI Debate Arena. The topic is: {self.topic}")

        # Main Debate Loop
        self.current_phase = DebatePhase.OPENING_STATEMENTS
        while self.current_phase != DebatePhase.COMPLETE:
            await self._run_phase()
            self.current_phase = self.protocol.get_next_phase(self.current_phase)

        # Wrap up
        await self._broadcast("The debate has concluded. Thank you all.")

        return {
            "topic": self.topic,
            "history": [m.to_dict() for m in self.history],
            "synthesis": {},  # Placeholder for synthesis result
        }

    async def _run_phase(self):
        """Execute the current phase."""
        config = self.protocol.get_phase_config(self.current_phase)
        if not config:
            return

        logger.info(f"Starting phase: {config.name}")
        await self._broadcast(f"Starting phase: {config.name}. {config.description}")

        if self.current_phase == DebatePhase.OPENING_STATEMENTS:
            await self._run_sequential_turns()
        elif self.current_phase == DebatePhase.FIRST_REBUTTALS:
            # Reverse order for rebuttals
            self.participants.reverse()
            await self._run_sequential_turns()
            self.participants.reverse()  # Restore order
        elif self.current_phase == DebatePhase.CROSS_EXAMINATION:
            await self._run_cross_examination()
        elif self.current_phase == DebatePhase.CLOSING_ARGUMENTS:
            await self._run_sequential_turns()
        elif self.current_phase == DebatePhase.SYNTHESIS:
            if self.synthesizer:
                await self._run_synthesis()

    async def _run_sequential_turns(self):
        """Give each participant a turn."""
        for agent in self.participants:
            await self._broadcast(f"{agent.name}, it is your turn.")

            # Construct context from history
            context = self._get_context_for_agent(agent)
            prompt = f"It is your turn in the {self.current_phase} phase. The topic is '{self.topic}'. Please provide your input."

            response_text = await agent.generate_response(context, prompt)

            message = self._create_message(
                content=response_text,
                msg_type=MessageType.ARGUMENT,  # Default to argument
                to_agent=None,  # Broadcast
            )
            # Override from_agent since _create_message uses self.name
            message["from_agent"] = agent.name
            message["role"] = agent.role

            # Store and broadcast
            debate_msg = DebateMessage(**message)
            self.history.append(debate_msg)
            logger.info(f"{agent.name}: {response_text}")

            # Simulate real-time fact checking (async in future)
            if self.fact_checker:
                # TODO: Trigger fact check
                pass

    async def _run_cross_examination(self):
        """Round-robin questioning."""
        # Simplified for MVP: Each agent asks one question to the other
        if len(self.participants) < 2:
            return

        agent_a = self.participants[0]
        agent_b = self.participants[1]

        # A asks B
        await self._facilitate_qa(agent_a, agent_b)
        # B asks A
        await self._facilitate_qa(agent_b, agent_a)

    async def _facilitate_qa(self, asker, answerer):
        """Manage Q&A interaction."""
        await self._broadcast(f"{asker.name}, please ask a question to {answerer.name}.")

        # Ask
        context = self._get_context_for_agent(asker)
        q_prompt = (
            f"Ask a critical question to {answerer.name} about their position on '{self.topic}'."
        )
        question_text = await asker.generate_response(context, q_prompt)

        q_msg = DebateMessage(**self._create_message(question_text, MessageType.QUESTION))
        q_msg.from_agent = asker.name
        q_msg.role = asker.role
        self.history.append(q_msg)
        logger.info(f"{asker.name} asks: {question_text[:100]}")

        # Answer
        await self._broadcast(f"{answerer.name}, please answer.")
        context = self._get_context_for_agent(answerer)
        a_prompt = f"Answer the question from {asker.name}: '{question_text}'"
        answer_text = await answerer.generate_response(context, a_prompt)

        a_msg = DebateMessage(**self._create_message(answer_text, MessageType.ANSWER))
        a_msg.from_agent = answerer.name
        a_msg.role = answerer.role
        self.history.append(a_msg)
        logger.info(f"{answerer.name} answers: {answer_text[:100]}")

    async def _run_synthesis(self):
        """Trigger synthesis agent."""
        await self._broadcast("Synthesizer, please analyze the debate.")
        context = self._get_full_history()
        prompt = f"Analyze the debate on '{self.topic}' and provide a synthesis."

        synthesis_text = await self.synthesizer.generate_response(context, prompt)

        msg = DebateMessage(**self._create_message(synthesis_text, MessageType.SYNTHESIS))
        msg.from_agent = self.synthesizer.name
        msg.role = self.synthesizer.role
        self.history.append(msg)
        logger.info(f"Synthesis: {synthesis_text[:100]}")

    async def _broadcast(self, content: str):
        """Send a system message to all."""
        msg = self._create_message(content, MessageType.SYSTEM)
        debate_msg = DebateMessage(**msg)
        self.history.append(debate_msg)
        logger.info(f"[MODERATOR]: {content}")

    def _get_context_for_agent(self, agent: BaseDebateAgent) -> str:
        """Get relevant history for an agent."""
        # Simple MVP: Return last N messages or full history
        # TODO: Implement more sophisticated context windowing
        return "\n".join([f"{m.from_agent}: {m.content}" for m in self.history[-10:]])

    def _get_full_history(self) -> str:
        return "\n".join([f"{m.from_agent}: {m.content}" for m in self.history])

    async def validate_topic(self, topic: str) -> tuple[bool, str]:
        """
        Validate if the topic is appropriate for debate.
        Returns (is_valid, reason).
        """
        prompt = (
            f"Topic: {topic}\n"
            "Is this topic a valid, meaningful subject for a professional debate? "
            "It must be a clear question or statement, not gibberish, not hate speech, and not explicit. "
            "If it is nonsense or unclear, reject it. "
            "Reply with exactly 'VALID' if it is okay. "
            "If not, reply with 'INVALID: <reason>'."
        )
        # Use a short response
        response = await self.generate_response(context="", prompt=prompt)

        if response.strip().upper().startswith("VALID"):
            return True, ""
        else:
            reason = response.replace("INVALID:", "").strip()
            # Fallback if LLM is chatty
            if "VALID" in response.upper() and len(response) < 20:
                return True, ""
            return False, reason

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming messages (not used in main loop currently)."""
        return {}

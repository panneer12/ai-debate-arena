"""Devil's Advocate agent for AI Debate Arena."""

import logging
from typing import Any, Dict, List

from agents.base_agent import BaseDebateAgent
from protocols.message_format import DebateMessage, MessageType

logger = logging.getLogger(__name__)


class DevilsAdvocateAgent(BaseDebateAgent):
    """
    Agent that challenges all positions to prevent groupthink.

    Uses Socratic questioning to expose assumptions and test argument strength.
    """

    def __init__(self):
        super().__init__(name="Devil's Advocate", role="Critical Challenger")
        self.challenge_types = [
            "assumption",
            "logical_consistency",
            "counterexample",
            "alternative_explanation",
            "unintended_consequence",
        ]
        logger.info("✅ Devil's Advocate initialized")

    async def challenge_argument(self, argument: str, author: str) -> Dict[str, Any]:
        """
        Generate a critical challenge to an argument.

        Args:
            argument: The argument to challenge.
            author: The author of the argument.

        Returns:
            Dictionary with challenge type and content.
        """
        prompt = f"""You are a Devil's Advocate. Challenge this argument by {author}:

"{argument}"

Your goal: Identify the MOST FUNDAMENTAL weakness and challenge it with a probing question.

CHALLENGE TYPES (in priority order - choose the FIRST applicable one):

1. **assumption** - Hidden or unverified assumptions (HIGHEST PRIORITY)
   Use when: The argument takes something for granted without proof
   Example: "Free markets work best" → Challenge: "What evidence supports this works for ALL markets and ALL people?"

2. **logical_consistency** - Internal contradictions
   Use when: The argument contradicts itself
   Example: "Government bad, but need strong police" → Challenge: "How do you reconcile these opposing views?"

3. **counterexample** - Real-world cases that contradict the claim
   Use when: The argument makes absolute claims ("always", "never", "all")
   Example: "X always works" → Challenge: "What about countries where X failed?"

4. **alternative_explanation** - Other ways to explain the same facts
   Use when: The argument attributes causation without ruling out alternatives
   Example: "Crime dropped due to policy" → Challenge: "Could this be due to economic growth instead?"

5. **unintended_consequence** - Unexpected negative outcomes
   Use when: The argument proposes action without considering downsides
   Example: "Ban all guns" → Challenge: "What about black markets and enforcement issues?"

DECISION RULES:
- If the argument contains HIDDEN ASSUMPTIONS → choose "assumption"
- If the argument has INTERNAL CONTRADICTIONS → choose "logical_consistency"
- Otherwise, pick the most relevant from the remaining types

INSTRUCTIONS:
1. Read the argument carefully
2. Apply the decision rules above
3. Pick the FIRST applicable challenge type (highest priority wins)
4. Formulate a specific, probing question

Respond EXACTLY in this format:
CHALLENGE TYPE: [assumption|logical_consistency|counterexample|alternative_explanation|unintended_consequence]
QUESTION: [Your challenging question]
REASONING: [Why this challenge matters - 1 sentence]"""

        response = await self.generate_response("", prompt)

        # Parse response
        challenge_type, question, reasoning = self._parse_challenge_response(response)

        return {
            "argument": argument,
            "author": author,
            "challenge_type": challenge_type,
            "question": question,
            "reasoning": reasoning,
        }

    def _parse_challenge_response(self, response: str) -> tuple:
        """
        Parse the Devil's Advocate challenge response.

        Returns:
            Tuple of (challenge_type, question, reasoning)
        """
        lines = response.strip().split("\n")
        challenge_type = "assumption"  # Default
        question = ""
        reasoning = ""

        for line in lines:
            line_upper = line.upper()
            if "CHALLENGE TYPE:" in line_upper:
                challenge_type = line.split(":", 1)[1].strip().lower()
            elif "QUESTION:" in line_upper:
                question = line.split(":", 1)[1].strip()
            elif "REASONING:" in line_upper:
                reasoning = line.split(":", 1)[1].strip()

        # If question wasn't parsed, use full response
        if not question:
            question = response

        return challenge_type, question, reasoning

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming message and generate a challenge.

        Args:
            message: Incoming debate message.

        Returns:
            Challenge message.
        """
        content = message.get("content", "")
        author = message.get("from_agent", "Unknown")

        # Generate challenge
        result = await self.challenge_argument(content, author)

        challenge_summary = f"""🎭 **Devil's Advocate Challenge**
To: {author}
Type: {result['challenge_type'].replace('_', ' ').title()}

{result['question']}

Why this matters: {result['reasoning']}"""

        return self._create_message(
            content=challenge_summary, msg_type=MessageType.QUESTION, to_agent=author
        )

"""Devil's Advocate agent for AI Debate Arena."""
import logging
from typing import Dict, Any, List

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
            "unintended_consequence"
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
        prompt = f"""You are a Devil's Advocate. Your role is to challenge the following argument by {author}:

"{argument}"

Your job is to:
1. Identify hidden assumptions
2. Find logical inconsistencies
3. Present counterexamples
4. Suggest alternative explanations
5. Highlight potential unintended consequences

Be respectful but rigorous. Ask probing questions that expose weaknesses.

Format your response as:
CHALLENGE TYPE: [one of: assumption, logical_consistency, counterexample, alternative_explanation, unintended_consequence]
QUESTION: [your challenging question]
REASONING: [brief explanation of why this challenge matters]"""

        response = await self.generate_response("", prompt)
        
        # Parse response
        challenge_type, question, reasoning = self._parse_challenge_response(response)
        
        return {
            "argument": argument,
            "author": author,
            "challenge_type": challenge_type,
            "question": question,
            "reasoning": reasoning
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
            content=challenge_summary,
            msg_type=MessageType.QUESTION,
            to_agent=author
        )

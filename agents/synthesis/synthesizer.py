"""Synthesizer agent for AI Debate Arena."""

import logging
from typing import Any, Dict, List

from agents.base_agent import BaseDebateAgent
from protocols.message_format import DebateMessage, MessageType

logger = logging.getLogger(__name__)


class SynthesizerAgent(BaseDebateAgent):
    """
    Agent that aggregates debate points and generates final conclusions.

    Synthesizes arguments, identifies winning points, and provides a balanced summary.
    """

    def __init__(self):
        super().__init__(name="Synthesizer", role="Conclusion Generator")
        logger.info("✅ Synthesizer initialized")

    async def synthesize_debate(self, history: List[DebateMessage], topic: str) -> Dict[str, Any]:
        """
        Synthesize the debate history into a final conclusion.

        Args:
            history: List of debate messages.
            topic: The debate topic.

        Returns:
            Dictionary with synthesis results.
        """
        # Format history for the LLM
        transcript = "\n".join([f"{msg.from_agent} ({msg.role}): {msg.content}" for msg in history])

        prompt = f"""You are an expert Debate Synthesizer. Your task is to analyze the following debate on "{topic}" and provide a comprehensive conclusion.

TRANSCRIPT:
{transcript}

Analyze the debate and provide:
1. **Winner**: Who presented the stronger case? (Or "Draw" if balanced)
2. **Key Arguments**: The most impactful points made by each side.
3. **Common Ground**: Areas where both sides agreed or overlapped.
4. **Actionable Takeaways**: Practical steps or recommendations based on the debate.
5. **Confidence Score**: How confident are you in this synthesis? (0.0-1.0)

Format your response as:
WINNER: [Name or "Draw"]
KEY_ARGUMENTS:
- [Side A]: [Point 1]
- [Side B]: [Point 1]
COMMON_GROUND: [List of points]
TAKEAWAYS: [List of recommendations]
CONFIDENCE: [0.0-1.0]
SUMMARY: [Brief narrative summary of the debate outcome]"""

        response = await self.generate_response("", prompt)

        # Parse response
        synthesis = self._parse_synthesis_response(response)

        return {"topic": topic, **synthesis}

    def _parse_synthesis_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the synthesizer's response.

        Returns:
            Dictionary with parsed synthesis fields.
        """
        lines = response.strip().split("\n")

        result = {
            "winner": "Draw",
            "key_arguments": [],
            "common_ground": [],
            "takeaways": [],
            "confidence": 0.5,
            "summary": "",
        }

        current_section = None

        for line in lines:
            line_upper = line.upper()
            line_stripped = line.strip()

            if "WINNER:" in line_upper:
                result["winner"] = line.split(":", 1)[1].strip()
                current_section = None
            elif "KEY_ARGUMENTS:" in line_upper:
                current_section = "key_arguments"
            elif "COMMON_GROUND:" in line_upper:
                current_section = "common_ground"
            elif "TAKEAWAYS:" in line_upper:
                current_section = "takeaways"
            elif "CONFIDENCE:" in line_upper:
                try:
                    score = float(line.split(":", 1)[1].strip())
                    result["confidence"] = max(0.0, min(1.0, score))
                except (ValueError, IndexError):
                    pass
                current_section = None
            elif "SUMMARY:" in line_upper:
                result["summary"] = line.split(":", 1)[1].strip()
                current_section = "summary"  # Continue capturing summary if multi-line
            elif current_section and (
                line_stripped.startswith("-") or line_stripped.startswith("*")
            ):
                item = line_stripped.lstrip("-* ").strip()
                if current_section == "key_arguments":
                    result["key_arguments"].append(item)
                elif current_section == "common_ground":
                    result["common_ground"].append(item)
                elif current_section == "takeaways":
                    result["takeaways"].append(item)
            elif current_section == "summary" and line_stripped:
                result["summary"] += " " + line_stripped

        return result

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming message (usually not used for Synthesizer in real-time).

        Args:
            message: Incoming debate message.

        Returns:
            Empty response or acknowledgment.
        """
        # Synthesizer typically runs at the end, but could provide interim summaries
        return self._create_message(
            content="Synthesizer is observing.", msg_type=MessageType.SYSTEM, to_agent=None
        )

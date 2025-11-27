"""Common Ground Finder agent for AI Debate Arena."""
import logging
from typing import Dict, Any, List

from agents.base_agent import BaseDebateAgent
from protocols.message_format import DebateMessage, MessageType

logger = logging.getLogger(__name__)

class CommonGroundFinder(BaseDebateAgent):
    """
    Agent that identifies shared values and agreements between debaters.
    
    Analyzes debate history to find overlapping principles, agreed facts, and shared goals.
    """
    
    def __init__(self):
        super().__init__(name="Common Ground Finder", role="Mediator")
        logger.info("✅ Common Ground Finder initialized")

    async def find_common_ground(self, history: List[DebateMessage], topic: str) -> Dict[str, Any]:
        """
        Analyze debate history for common ground.
        
        Args:
            history: List of debate messages.
            topic: The debate topic.
            
        Returns:
            Dictionary with common ground analysis.
        """
        # Format history for the LLM
        transcript = "\n".join([f"{msg.from_agent} ({msg.role}): {msg.content}" for msg in history])
        
        prompt = f"""You are an expert Mediator. Your task is to analyze the following debate on "{topic}" and identify ALL areas of agreement and shared values.

TRANSCRIPT:
{transcript}

Analyze the debate and identify:
1. **Shared Values**: Underlying principles both sides care about (e.g., "Safety", "Freedom", "Prosperity").
2. **Agreed Facts**: Factual points that neither side disputed.
3. **Convergent Solutions**: Policy ideas where both sides might agree or compromise.
4. **Agreement Score**: A score from 0-100 indicating how much overlap exists.

Format your response as:
SHARED_VALUES: [Comma-separated list]
AGREED_FACTS:
- [Fact 1]
- [Fact 2]
CONVERGENT_SOLUTIONS:
- [Solution 1]
AGREEMENT_SCORE: [0-100]
ANALYSIS: [Brief explanation of the alignment]"""

        response = await self.generate_response("", prompt)
        
        # Parse response
        analysis = self._parse_common_ground_response(response)
        
        return {
            "topic": topic,
            **analysis
        }

    def _parse_common_ground_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the common ground finder's response.

        Returns:
            Dictionary with parsed analysis fields.
        """
        if not response:
            return {
                "shared_values": [],
                "agreed_facts": [],
                "convergent_solutions": [],
                "agreement_score": 0,
                "analysis": "No response generated"
            }

        lines = response.strip().split("\n")
        
        result = {
            "shared_values": [],
            "agreed_facts": [],
            "convergent_solutions": [],
            "agreement_score": 0,
            "analysis": ""
        }
        
        current_section = None
        
        for line in lines:
            line_upper = line.upper()
            line_stripped = line.strip()
            
            if "SHARED_VALUES:" in line_upper:
                values_str = line.split(":", 1)[1].strip()
                result["shared_values"] = [v.strip() for v in values_str.split(",") if v.strip()]
                current_section = None
            elif "AGREED_FACTS:" in line_upper:
                current_section = "agreed_facts"
            elif "CONVERGENT_SOLUTIONS:" in line_upper:
                current_section = "convergent_solutions"
            elif "AGREEMENT_SCORE:" in line_upper:
                try:
                    score_str = line.split(":", 1)[1].strip().replace("%", "")
                    result["agreement_score"] = int(score_str)
                except (ValueError, IndexError):
                    pass
                current_section = None
            elif "ANALYSIS:" in line_upper:
                result["analysis"] = line.split(":", 1)[1].strip()
                current_section = "analysis"
            elif current_section and (line_stripped.startswith("-") or line_stripped.startswith("*")):
                item = line_stripped.lstrip("-* ").strip()
                if current_section == "agreed_facts":
                    result["agreed_facts"].append(item)
                elif current_section == "convergent_solutions":
                    result["convergent_solutions"].append(item)
            elif current_section == "analysis" and line_stripped:
                result["analysis"] += " " + line_stripped
        
        return result

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming message (usually not used for Common Ground Finder in real-time).
        
        Args:
            message: Incoming debate message.
            
        Returns:
            Empty response or acknowledgment.
        """
        return self._create_message(
            content="Common Ground Finder is observing.",
            msg_type=MessageType.SYSTEM,
            to_agent=None
        )

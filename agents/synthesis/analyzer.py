"""Argument analyzer agent for AI Debate Arena."""

import logging
from typing import Any, Dict, List

from agents.base_agent import BaseDebateAgent
from protocols.message_format import DebateMessage, MessageType

logger = logging.getLogger(__name__)


class ArgumentAnalyzerAgent(BaseDebateAgent):
    """
    Agent that analyzes arguments for logical validity and fallacies.

    Evaluates argument structure, identifies fallacies, and provides quality scores.
    """

    def __init__(self):
        super().__init__(name="Argument Analyzer", role="Logic Evaluator")
        self.fallacy_types = [
            "ad_hominem",
            "straw_man",
            "false_dichotomy",
            "slippery_slope",
            "appeal_to_authority",
            "circular_reasoning",
            "hasty_generalization",
            "red_herring",
        ]
        logger.info("✅ Argument Analyzer initialized")

    async def analyze_argument(self, argument: str, author: str) -> Dict[str, Any]:
        """
        Analyze an argument for logical validity and fallacies.

        Args:
            argument: The argument to analyze.
            author: The author of the argument.

        Returns:
            Dictionary with analysis results.
        """
        prompt = f"""Analyze the following argument by {author} for logical validity:

"{argument}"

IMPORTANT DISTINCTION - Legitimate vs Fallacious:
- Citing experts IN THEIR FIELD is LEGITIMATE (e.g., "Climate scientists say..." about climate)
- Citing experts OUTSIDE THEIR FIELD is FALLACIOUS (e.g., "A celebrity says..." about medicine)
- Personal attacks INSTEAD OF addressing argument = ad_hominem FALLACY
- Simply identifying someone's credentials is NOT a fallacy

COMMON FALLACIES (only list if clearly present):
1. **ad_hominem** - Attacking the person instead of their argument
   Example: "You're wrong because you're biased" (attacks person, not argument)
   
2. **straw_man** - Misrepresenting someone's argument to make it easier to attack
   
3. **false_dichotomy** - Presenting only two options when more exist
   
4. **appeal_to_authority** - Citing irrelevant or unqualified authorities
   NOTE: Citing RELEVANT experts (scientists for science, economists for economy) is VALID, not a fallacy!

5. **hasty_generalization** - Drawing broad conclusions from limited evidence

Evaluate:
1. **Logical Structure**: Is the reasoning sound? (0.0-1.0)
2. **Evidence Quality**: Is it well-supported? (0.0-1.0)
3. **Fallacies**: List ONLY THE PRIMARY fallacy if one exists, otherwise "none"
4. **Strengths**: What makes this argument strong?
5. **Weaknesses**: What undermines this argument?

DECISION RULES:
- If the argument cites RELEVANT experts with data → fallacies = "none"
- If the argument attacks the person INSTEAD of the argument → fallacies = "ad_hominem"
- Only list the MOST SIGNIFICANT fallacy, not all possible ones

Format your response as:
LOGICAL_VALIDITY: [0.0-1.0]
EVIDENCE_QUALITY: [0.0-1.0]
FALLACIES: [single fallacy name or "none"]
STRENGTHS: [brief list]
WEAKNESSES: [brief list]"""

        response = await self.generate_response("", prompt)

        # Parse response
        analysis = self._parse_analysis_response(response)

        return {"argument": argument, "author": author, **analysis}

    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the analyzer's response.

        Returns:
            Dictionary with parsed analysis fields.
        """
        lines = response.strip().split("\n")

        result = {
            "logical_validity": 0.5,
            "evidence_quality": 0.5,
            "fallacies": [],
            "strengths": "",
            "weaknesses": "",
        }

        for line in lines:
            line_upper = line.upper()

            if "LOGICAL_VALIDITY:" in line_upper or "LOGICAL STRUCTURE:" in line_upper:
                try:
                    score = float(line.split(":", 1)[1].strip())
                    result["logical_validity"] = max(0.0, min(1.0, score))
                except (ValueError, IndexError):
                    pass

            elif "EVIDENCE_QUALITY:" in line_upper or "EVIDENCE QUALITY:" in line_upper:
                try:
                    score = float(line.split(":", 1)[1].strip())
                    result["evidence_quality"] = max(0.0, min(1.0, score))
                except (ValueError, IndexError):
                    pass

            elif "FALLACIES:" in line_upper or "FALLACY:" in line_upper:
                fallacies_str = line.split(":", 1)[1].strip().lower()
                if "none" not in fallacies_str:
                    result["fallacies"] = [f.strip() for f in fallacies_str.split(",")]

            elif "STRENGTHS:" in line_upper or "STRENGTH:" in line_upper:
                result["strengths"] = line.split(":", 1)[1].strip()

            elif "WEAKNESSES:" in line_upper or "WEAKNESS:" in line_upper:
                result["weaknesses"] = line.split(":", 1)[1].strip()

        return result

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming message and analyze the argument.

        Args:
            message: Incoming debate message.

        Returns:
            Analysis result message.
        """
        content = message.get("content", "")
        author = message.get("from_agent", "Unknown")

        # Analyze the argument
        result = await self.analyze_argument(content, author)

        # Format fallacies
        fallacies_str = ", ".join(result["fallacies"]) if result["fallacies"] else "None detected"

        analysis_summary = f"""📊 **Argument Analysis for {author}**

**Quality Scores:**
- Logical Validity: {result['logical_validity']:.0%}
- Evidence Quality: {result['evidence_quality']:.0%}

**Fallacies Detected:** {fallacies_str}

**Strengths:** {result['strengths']}

**Weaknesses:** {result['weaknesses']}"""

        return self._create_message(
            content=analysis_summary, msg_type=MessageType.SYSTEM, to_agent=None  # Broadcast
        )

"""Argument analyzer agent for AI Debate Arena."""
import logging
from typing import Dict, Any, List

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
            "red_herring"
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

Evaluate:
1. **Logical Structure**: Is the reasoning sound? (0.0-1.0)
2. **Evidence Quality**: Is it well-supported? (0.0-1.0)
3. **Fallacies**: Identify any logical fallacies present
4. **Strengths**: What makes this argument strong?
5. **Weaknesses**: What undermines this argument?

Format your response as:
LOGICAL_VALIDITY: [0.0-1.0]
EVIDENCE_QUALITY: [0.0-1.0]
FALLACIES: [comma-separated list or "none"]
STRENGTHS: [brief list]
WEAKNESSES: [brief list]"""

        response = await self.generate_response("", prompt)
        
        # Parse response
        analysis = self._parse_analysis_response(response)
        
        return {
            "argument": argument,
            "author": author,
            **analysis
        }

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
            "weaknesses": ""
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
            content=analysis_summary,
            msg_type=MessageType.SYSTEM,
            to_agent=None  # Broadcast
        )

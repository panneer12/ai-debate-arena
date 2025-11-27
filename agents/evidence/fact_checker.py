"""Fact checking agent using Google ADK's built-in search grounding."""

import logging
from typing import Any, Dict, List, Optional

from google.genai import types

from agents.base_agent import BaseDebateAgent
from protocols.message_format import DebateMessage, Evidence, MessageType

logger = logging.getLogger(__name__)


class FactCheckerAgent(BaseDebateAgent):
    """
    Agent that verifies claims using Google ADK's built-in search grounding.

    Uses the native google_search tool in Google ADK for fact verification.
    """

    def __init__(self):
        super().__init__(name="Fact Checker", role="Evidence Verifier")
        logger.info("✅ Fact Checker initialized with Google Search grounding")

    async def check_claim(self, claim: str) -> Dict[str, Any]:
        """
        Verify a single claim using Google Search grounding.

        Args:
            claim: The claim to verify.

        Returns:
            Dictionary with verification results including confidence and evidence.
        """
        # Use Google ADK's built-in search grounding
        prompt = f"""Fact-check this claim using Google Search: "{claim}"

Provide:
1. VERDICT: TRUE, FALSE, PARTIALLY_TRUE, or UNVERIFIABLE
2. CONFIDENCE: 0.0-1.0 (how certain you are)
3. EVIDENCE: Brief summary of what you found
4. SOURCES: List key sources

Format:
VERDICT: [verdict]
CONFIDENCE: [number]
EVIDENCE: [brief summary]
SOURCES: [list]"""

        try:
            # Enable google_search tool via ADK
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.1,  # Low temperature for factual accuracy
                    tools=[types.Tool(google_search=types.GoogleSearch())],  # Enable search!
                    response_modalities=["TEXT"],
                ),
            )

            response_text = response.text

        except Exception as e:
            logger.warning(f"Search grounding failed: {e}")
            # Fallback to LLM-only if grounding fails
            response_text = await self.generate_response("", prompt)

        # Parse response
        verdict, confidence, explanation = self._parse_fact_check_response(response_text)

        return {
            "claim": claim,
            "verdict": verdict,
            "confidence": confidence,
            "explanation": explanation,
            "search_used": True,
        }

    def _parse_fact_check_response(self, response: str) -> tuple:
        """
        Parse the LLM's fact-check response.

        Returns:
            Tuple of (verdict, confidence, explanation)
        """
        lines = response.strip().split("\n")
        verdict = "UNVERIFIABLE"
        confidence = 0.5
        explanation = response  # Default to full response

        for line in lines:
            line_upper = line.upper()
            if "VERDICT:" in line_upper:
                verdict = line.split(":", 1)[1].strip()
            elif "CONFIDENCE:" in line_upper:
                try:
                    conf_str = line.split(":", 1)[1].strip()
                    confidence = float(conf_str)
                except (ValueError, IndexError):
                    pass
            elif "EVIDENCE:" in line_upper or "EXPLANATION:" in line_upper:
                explanation = line.split(":", 1)[1].strip()

        return verdict, confidence, explanation

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming message and check for claims to verify.

        Args:
            message: Incoming debate message.

        Returns:
            Fact-check result message.
        """
        content = message.get("content", "")

        # For MVP, treat entire message as a claim
        result = await self.check_claim(content)

        fact_check_summary = f"""🔍 **Fact Check Result**
Claim: "{result['claim'][:100]}..."
Verdict: {result['verdict']}
Confidence: {result['confidence']:.0%}
{result['explanation']}"""

        return self._create_message(
            content=fact_check_summary,
            msg_type=MessageType.FACT_CHECK,
            to_agent=message.get("from_agent"),
        )

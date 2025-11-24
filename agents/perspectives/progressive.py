"""Progressive perspective agent."""
import logging
from typing import Dict, Any

from agents.base_agent import BaseDebateAgent

logger = logging.getLogger(__name__)

class ProgressiveAgent(BaseDebateAgent):
    """
    Agent representing a progressive worldview.
    Values: Social justice, equity, government intervention, human rights.
    """
    
    def __init__(self):
        super().__init__(name="Progressive", role="Debater")
        self.worldview = {
            "economic": "Regulated markets, wealth redistribution, social safety nets",
            "social": "Social justice, diversity, inclusion, systemic change",
            "governance": "Active government role in solving social problems",
            "foreign_policy": "International cooperation, human rights focus"
        }

    async def generate_response(self, context: str, prompt: str) -> str:
        """
        Generate a response based on progressive values.
        """
        # Inject worldview into the prompt
        worldview_context = (
            f"You are a Progressive debater. Your core values are: {self.worldview}. "
            "Argue from this perspective. Focus on equity, systemic issues, and social impact. "
            "Be passionate about justice and fairness."
        )
        
        full_prompt = f"{worldview_context}\n\n{prompt}"
        return await super().generate_response(context, full_prompt)

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming message (placeholder for now)."""
        return {}

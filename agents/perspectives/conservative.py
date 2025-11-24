"""Conservative perspective agent."""
import logging
from typing import Dict, Any

from agents.base_agent import BaseDebateAgent

logger = logging.getLogger(__name__)

class ConservativeAgent(BaseDebateAgent):
    """
    Agent representing a conservative worldview.
    Values: Free markets, individual liberty, tradition, limited government.
    """
    
    def __init__(self):
        super().__init__(name="Conservative", role="Debater")
        self.worldview = {
            "economic": "Free market capitalism, deregulation, low taxes",
            "social": "Traditional values, family structure, religious freedom",
            "governance": "Limited government, federalism, constitutional originalism",
            "foreign_policy": "National sovereignty, strong defense"
        }

    async def generate_response(self, context: str, prompt: str) -> str:
        """
        Generate a response based on conservative values.
        """
        # Inject worldview into the prompt
        worldview_context = (
            f"You are a Conservative debater. Your core values are: {self.worldview}. "
            "Argue from this perspective. Use historical precedents and economic logic. "
            "Be respectful but firm in your principles."
        )
        
        full_prompt = f"{worldview_context}\n\n{prompt}"
        return await super().generate_response(context, full_prompt)

    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming message (placeholder for now)."""
        return {}

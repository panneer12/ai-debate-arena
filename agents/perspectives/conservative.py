"""Conservative perspective agent."""

import logging
from typing import Any, Dict

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
            "foreign_policy": "National sovereignty, strong defense",
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
        """Process incoming message."""
        from protocols.message_format import MessageType

        # Extract content from previous message
        incoming_content = message.get("content", "")
        prompt = f"Respond to the following argument: '{incoming_content}'"

        # Generate response
        # Note: In a real system, we would pass more history as context
        response_text = await self.generate_response("", prompt)

        return self._create_message(response_text, MessageType.ARGUMENT)

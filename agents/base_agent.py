"""Base agent class for AI Debate Arena."""
import abc
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from google import genai
from google.genai import types

from config import settings

logger = logging.getLogger(__name__)

class BaseDebateAgent(abc.ABC):
    """
    Abstract base class for all debate agents.
    
    Attributes:
        name (str): The name of the agent.
        role (str): The role of the agent (e.g., "Debater", "Moderator").
        model (genai.GenerativeModel): The Gemini model instance.
    """

    def __init__(self, name: str, role: str):
        """
        Initialize the base agent.

        Args:
            name: Name of the agent.
            role: Role of the agent.
        """
        self.name = name
        self.role = role
        self.id = str(uuid.uuid4())
        
        # Initialize Gemini client
        self.client = genai.Client(api_key=settings.google_api_key)
        self.model_name = settings.llm_model
        
        logger.info(f"Initialized agent {self.name} ({self.role}) with model {self.model_name}")

    async def generate_response(self, context: str, prompt: str) -> str:
        """
        Generate a response using the LLM.

        Args:
            context: The context of the debate so far.
            prompt: The specific prompt for this turn.

        Returns:
            The generated response text.
        """
        try:
            full_prompt = f"{context}\n\n{prompt}"
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    temperature=settings.llm_temperature,
                    max_output_tokens=settings.llm_max_tokens
                )
            )
            
            return response.text
        except Exception as e:
            logger.error(f"Error generating response for {self.name}: {e}")
            raise

    @abc.abstractmethod
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming message and determine the action.

        Args:
            message: The incoming message dictionary.

        Returns:
            The response message dictionary.
        """
        pass

    def _create_message(self, content: str, msg_type: str, to_agent: Optional[str] = None) -> Dict[str, Any]:
        """
        Helper to create a standardized message.
        
        Args:
            content: The text content of the message.
            msg_type: The type of message (e.g., "ARGUMENT", "REBUTTAL").
            to_agent: Optional ID of the recipient agent.
            
        Returns:
            A dictionary representing the message.
        """
        return {
            "id": str(uuid.uuid4()),
            "type": msg_type,
            "from_agent": self.name,
            "to_agent": to_agent,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "role": self.role
        }

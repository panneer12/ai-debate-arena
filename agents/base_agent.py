"""Base agent class for AI Debate Arena."""
import abc
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import time

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

    async def generate_response(self, context: str, prompt: str, metrics_collector: Optional[Any] = None) -> str:
        """
        Generate a response using the LLM with retry logic and fallback model.

        Args:
            context: The context of the debate so far.
            prompt: The specific prompt for this turn.
            metrics_collector: Optional MetricsCollector instance.

        Returns:
            The generated response text.
        """
        import asyncio
        start_time = time.time()

        # Add word limit instruction to keep responses concise
        word_limit_instruction = "\n\nIMPORTANT: Keep your response concise and focused. Aim for 200-300 words maximum."
        full_prompt = f"{context}\n\n{prompt}{word_limit_instruction}"

        response_text = ""
        error = None

        try:
            # Try primary model with retries
            for attempt in range(settings.retry_attempts):
                try:
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=full_prompt,
                        config=types.GenerateContentConfig(
                            temperature=settings.llm_temperature,
                            max_output_tokens=settings.llm_max_tokens
                        )
                    )
                    response_text = response.text
                    return response_text

                except Exception as e:
                    error = e
                    error_msg = str(e)

                    # Handle server overload (503)
                    if "503" in error_msg or "UNAVAILABLE" in error_msg or "overloaded" in error_msg.lower():
                        if attempt < settings.retry_attempts - 1:
                            wait_time = settings.retry_delay_seconds * (attempt + 1)
                            logger.warning(f"⚠️ Server overloaded for {self.name}, retrying in {wait_time}s... (attempt {attempt + 1}/{settings.retry_attempts})")
                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            # Try fallback model
                            logger.warning(f"⚠️ Trying fallback model {settings.llm_fallback_model} for {self.name}")
                            try:
                                response = self.client.models.generate_content(
                                    model=settings.llm_fallback_model,
                                    contents=full_prompt,
                                    config=types.GenerateContentConfig(
                                        temperature=settings.llm_temperature,
                                        max_output_tokens=settings.llm_max_tokens
                                    )
                                )
                                response_text = response.text
                                return response_text
                            except Exception as fallback_error:
                                logger.error(f"❌ Fallback model also failed for {self.name}: {fallback_error}")
                                return f"[{self.name} - Server overloaded. Please try again in a moment.]"

                    # Handle quota exhausted errors
                    elif "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                        logger.warning(f"⚠️ API quota exceeded for {self.name}")
                        return f"[{self.name} - API quota exceeded. Please wait and try again, or upgrade your API plan.]"

                    # Handle network/connectivity errors
                    elif "connection" in error_msg.lower() or "timeout" in error_msg.lower():
                        if attempt < settings.retry_attempts - 1:
                            logger.warning(f"⚠️ Network error for {self.name}, retrying... (attempt {attempt + 1}/{settings.retry_attempts})")
                            await asyncio.sleep(settings.retry_delay_seconds)
                            continue
                        logger.warning(f"⚠️ Network error for {self.name}: {error_msg}")
                        return f"[{self.name} - Network error. Please check your connection.]"

                    # Handle authentication errors
                    elif "401" in error_msg or "UNAUTHENTICATED" in error_msg:
                        logger.error(f"❌ Invalid API key for {self.name}")
                        return f"[{self.name} - Invalid API key. Please check your GOOGLE_API_KEY in .env file.]"

                    # Handle other errors
                    else:
                        logger.error(f"❌ Unexpected error for {self.name}: {e}")
                        return f"[{self.name} - An unexpected error occurred: {type(e).__name__}]"

            # If all retries exhausted
            return f"[{self.name} - Failed after {settings.retry_attempts} attempts]"

        finally:
            if metrics_collector:
                metrics_collector.track_action(
                    agent_name=self.name,
                    action_type="generate_response",
                    start_time=start_time,
                    input_text=full_prompt,
                    output_text=response_text,
                    error=error
                )

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

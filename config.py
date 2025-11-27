"""Configuration settings for AI Debate Arena."""

import os
from typing import Optional

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    google_api_key: str
    google_search_api_key: Optional[str] = None
    google_search_engine_id: Optional[str] = None

    # LLM Configuration
    llm_model: str = "gemini-2.5-flash-lite"  # Using stable model with fallback
    llm_fallback_model: str = "gemini-2.5-flash"  # Lighter fallback
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1024

    # Rate Limiting
    agent_delay_seconds: float = 1.0  # Delay between agent calls
    retry_attempts: int = 3
    retry_delay_seconds: float = 2.0

    # Debate Configuration
    max_debate_rounds: int = 5
    opening_statement_seconds: int = 120
    rebuttal_seconds: int = 60
    closing_seconds: int = 90

    # Performance
    agent_timeout_seconds: int = 30
    fact_check_timeout_seconds: int = 10

    # Logging
    log_level: str = "INFO"
    log_format: str = "detailed"

    # Server (Cloud Run uses PORT env var)
    port: int = int(os.getenv("PORT", "8080"))
    host: str = "0.0.0.0"

    # Cache
    enable_fact_cache: bool = True
    fact_cache_ttl_days: int = 7

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

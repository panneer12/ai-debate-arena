"""Message protocol for AI Debate Arena."""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Types of messages exchanged in the debate."""

    OPENING_STATEMENT = "OPENING_STATEMENT"
    CLAIM = "CLAIM"
    ARGUMENT = "ARGUMENT"
    REBUTTAL = "REBUTTAL"
    QUESTION = "QUESTION"
    ANSWER = "ANSWER"
    FACT_CHECK = "FACT_CHECK"
    SYNTHESIS = "SYNTHESIS"
    SYSTEM = "SYSTEM"  # For moderator instructions


class Evidence(BaseModel):
    """Evidence supporting a claim."""

    source: str
    content: str
    credibility_score: float = Field(default=0.0, ge=0.0, le=1.0)
    url: Optional[str] = None


class DebateMessage(BaseModel):
    """Standard message format for agent communication."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType
    from_agent: str
    to_agent: Optional[str] = None  # None means broadcast to all
    content: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence: List[Evidence] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    round_number: int = 0
    role: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return self.model_dump(mode="json")

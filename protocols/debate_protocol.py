"""Debate protocol and flow management."""

from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel

from config import settings


class DebatePhase(str, Enum):
    """Phases of a formal debate."""

    SETUP = "SETUP"
    OPENING_STATEMENTS = "OPENING_STATEMENTS"
    FIRST_REBUTTALS = "FIRST_REBUTTALS"
    CROSS_EXAMINATION = "CROSS_EXAMINATION"
    SECOND_REBUTTALS = "SECOND_REBUTTALS"
    CLOSING_ARGUMENTS = "CLOSING_ARGUMENTS"
    SYNTHESIS = "SYNTHESIS"
    COMPLETE = "COMPLETE"


class PhaseConfig(BaseModel):
    """Configuration for a debate phase."""

    name: DebatePhase
    duration_seconds: int
    description: str


class DebateProtocol:
    """Manages the rules and flow of the debate."""

    def __init__(self):
        self.phases = {
            DebatePhase.OPENING_STATEMENTS: PhaseConfig(
                name=DebatePhase.OPENING_STATEMENTS,
                duration_seconds=settings.opening_statement_seconds,
                description="Present initial positions without interruption.",
            ),
            DebatePhase.FIRST_REBUTTALS: PhaseConfig(
                name=DebatePhase.FIRST_REBUTTALS,
                duration_seconds=settings.rebuttal_seconds,
                description="Address opponent's claims and present counter-evidence.",
            ),
            DebatePhase.CROSS_EXAMINATION: PhaseConfig(
                name=DebatePhase.CROSS_EXAMINATION,
                duration_seconds=180,  # 3 minutes total for cross-exam
                description="Ask and answer direct questions.",
            ),
            DebatePhase.CLOSING_ARGUMENTS: PhaseConfig(
                name=DebatePhase.CLOSING_ARGUMENTS,
                duration_seconds=settings.closing_seconds,
                description="Summarize key points and final appeal.",
            ),
        }

    def get_phase_config(self, phase: DebatePhase) -> PhaseConfig:
        """Get configuration for a specific phase."""
        return self.phases.get(phase)

    def get_next_phase(self, current_phase: DebatePhase) -> DebatePhase:
        """Determine the next phase in the debate flow."""
        order = [
            DebatePhase.SETUP,
            DebatePhase.OPENING_STATEMENTS,
            DebatePhase.FIRST_REBUTTALS,
            DebatePhase.CROSS_EXAMINATION,
            DebatePhase.CLOSING_ARGUMENTS,
            DebatePhase.SYNTHESIS,
            DebatePhase.COMPLETE,
        ]

        try:
            current_index = order.index(current_phase)
            if current_index < len(order) - 1:
                return order[current_index + 1]
        except ValueError:
            pass

        return DebatePhase.COMPLETE

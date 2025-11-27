"""Test Moderator Agent."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.base_agent import BaseDebateAgent
from agents.moderator import ModeratorAgent
from protocols.debate_protocol import DebatePhase


class MockAgent(BaseDebateAgent):
    def __init__(self, name, role):
        self.name = name
        self.role = role
        self.generate_response = AsyncMock(return_value="Mocked Argument")

    async def process_message(self, message):
        pass


@pytest.mark.asyncio
async def test_moderator_initialization():
    mod = ModeratorAgent()
    assert mod.name == "Moderator"
    assert mod.current_phase == DebatePhase.SETUP


@pytest.mark.asyncio
async def test_debate_flow():
    """Test a full debate cycle with mocked agents."""
    mod = ModeratorAgent()

    # Mock broadcast to avoid print spam
    mod._broadcast = AsyncMock()

    agent1 = MockAgent("Con", "Conservative")
    agent2 = MockAgent("Prog", "Progressive")

    # Mock the protocol to speed up tests (reduce phases)
    # We'll just test Opening -> Complete for simplicity in this unit test
    # or let it run through all phases but they are fast because of mocks

    result = await mod.start_debate(topic="Test Topic", debaters=[agent1, agent2])

    assert result["topic"] == "Test Topic"
    assert len(result["history"]) > 0

    # Verify phases were transitioned
    assert mod.current_phase == DebatePhase.COMPLETE

    # Verify agents were called
    assert agent1.generate_response.call_count >= 1
    assert agent2.generate_response.call_count >= 1


@pytest.mark.asyncio
async def test_cross_examination():
    """Test cross-examination logic."""
    mod = ModeratorAgent()
    mod._broadcast = AsyncMock()
    mod.current_phase = DebatePhase.CROSS_EXAMINATION
    mod.topic = "Test"

    agent1 = MockAgent("A", "RoleA")
    agent2 = MockAgent("B", "RoleB")
    mod.participants = [agent1, agent2]

    await mod._run_cross_examination()

    # A asks B, B answers A
    # B asks A, A answers B
    # Total 4 calls (2 questions, 2 answers)
    assert agent1.generate_response.call_count == 2
    assert agent2.generate_response.call_count == 2

"""Test Common Ground Finder Agent."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.synthesis.common_ground import CommonGroundFinder
from protocols.message_format import DebateMessage, MessageType


@pytest.fixture
def mock_genai_client():
    with patch("google.genai.Client") as mock:
        yield mock


@pytest.mark.asyncio
async def test_common_ground_initialization(mock_genai_client):
    """Test that common ground finder initializes correctly."""
    finder = CommonGroundFinder()
    assert finder.name == "Common Ground Finder"
    assert finder.role == "Mediator"


@pytest.mark.asyncio
async def test_find_common_ground(mock_genai_client):
    """Test finding common ground in a debate."""
    finder = CommonGroundFinder()

    # Mock LLM response
    mock_response = MagicMock()
    mock_response.text = """SHARED_VALUES: Safety, Economic Stability
AGREED_FACTS:
- Unemployment is rising
- Inflation is a concern
CONVERGENT_SOLUTIONS:
- Job training programs
AGREEMENT_SCORE: 65
ANALYSIS: Both sides agree on the economic problems but differ on solutions."""
    finder.client.models.generate_content.return_value = mock_response

    history = [
        DebateMessage(
            from_agent="Conservative",
            role="Debater",
            content="We need jobs",
            type=MessageType.ARGUMENT,
        ),
        DebateMessage(
            from_agent="Progressive",
            role="Debater",
            content="We need stability",
            type=MessageType.ARGUMENT,
        ),
    ]

    result = await finder.find_common_ground(history, "Economy")

    assert result["topic"] == "Economy"
    assert "Safety" in result["shared_values"]
    assert len(result["agreed_facts"]) == 2
    assert result["agreement_score"] == 65
    assert "Both sides agree" in result["analysis"]


@pytest.mark.asyncio
async def test_common_ground_parsing():
    """Test parsing of common ground responses."""
    finder = CommonGroundFinder()

    response = """SHARED_VALUES: Value 1, Value 2
AGREED_FACTS:
- Fact 1
CONVERGENT_SOLUTIONS:
- Solution 1
AGREEMENT_SCORE: 80
ANALYSIS: High alignment."""

    parsed = finder._parse_common_ground_response(response)

    assert parsed["shared_values"] == ["Value 1", "Value 2"]
    assert parsed["agreed_facts"] == ["Fact 1"]
    assert parsed["convergent_solutions"] == ["Solution 1"]
    assert parsed["agreement_score"] == 80

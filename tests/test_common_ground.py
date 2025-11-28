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


@pytest.mark.asyncio
async def test_common_ground_parsing_empty_response():
    """Test parsing empty response."""
    finder = CommonGroundFinder()

    parsed = finder._parse_common_ground_response("")

    assert parsed["shared_values"] == []
    assert parsed["agreed_facts"] == []
    assert parsed["convergent_solutions"] == []
    assert parsed["agreement_score"] == 0
    assert parsed["analysis"] == "No response generated"


@pytest.mark.asyncio
async def test_common_ground_parsing_with_asterisks():
    """Test parsing with asterisk bullet points."""
    finder = CommonGroundFinder()

    response = """SHARED_VALUES: Safety, Freedom
AGREED_FACTS:
* Economic challenges exist
* Change is needed
CONVERGENT_SOLUTIONS:
* Gradual reform
AGREEMENT_SCORE: 55
ANALYSIS: Moderate overlap."""

    parsed = finder._parse_common_ground_response(response)

    assert len(parsed["agreed_facts"]) == 2
    assert "Economic challenges exist" in parsed["agreed_facts"]
    assert len(parsed["convergent_solutions"]) == 1


@pytest.mark.asyncio
async def test_common_ground_parsing_multiline_analysis():
    """Test parsing with multiline analysis."""
    finder = CommonGroundFinder()

    response = """SHARED_VALUES: Justice, Equity
AGREED_FACTS:
- Current system has issues
CONVERGENT_SOLUTIONS:
- Incremental improvements
AGREEMENT_SCORE: 70
ANALYSIS: Both sides acknowledge problems.
They differ on solutions.
But share core values."""

    parsed = finder._parse_common_ground_response(response)

    assert "Both sides acknowledge problems" in parsed["analysis"]
    assert "They differ on solutions" in parsed["analysis"]
    assert "core values" in parsed["analysis"]


@pytest.mark.asyncio
async def test_common_ground_parsing_score_with_percent():
    """Test parsing agreement score with percent sign."""
    finder = CommonGroundFinder()

    response = """SHARED_VALUES: Test
AGREED_FACTS:
- Fact
CONVERGENT_SOLUTIONS:
- Solution
AGREEMENT_SCORE: 85%
ANALYSIS: Good."""

    parsed = finder._parse_common_ground_response(response)

    assert parsed["agreement_score"] == 85


@pytest.mark.asyncio
async def test_common_ground_parsing_invalid_score():
    """Test parsing with invalid agreement score."""
    finder = CommonGroundFinder()

    response = """SHARED_VALUES: Test
AGREEMENT_SCORE: invalid
ANALYSIS: Test."""

    parsed = finder._parse_common_ground_response(response)

    # Should default to 0
    assert parsed["agreement_score"] == 0


@pytest.mark.asyncio
async def test_process_message(mock_genai_client):
    """Test processing a message (common ground finder observes)."""
    finder = CommonGroundFinder()

    message = {
        "from_agent": "Progressive",
        "content": "Test argument",
        "type": "ARGUMENT",
    }

    result = await finder.process_message(message)

    assert result["type"] == "SYSTEM"
    assert "observing" in result["content"].lower()
    assert result["to_agent"] is None

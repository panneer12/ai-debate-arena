"""Test Synthesizer Agent."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.synthesis.synthesizer import SynthesizerAgent
from protocols.message_format import DebateMessage, MessageType


@pytest.fixture
def mock_genai_client():
    with patch("google.genai.Client") as mock:
        yield mock


@pytest.mark.asyncio
async def test_synthesizer_initialization(mock_genai_client):
    """Test that synthesizer initializes correctly."""
    synthesizer = SynthesizerAgent()
    assert synthesizer.name == "Synthesizer"
    assert synthesizer.role == "Conclusion Generator"


@pytest.mark.asyncio
async def test_synthesize_debate(mock_genai_client):
    """Test synthesizing a debate."""
    synthesizer = SynthesizerAgent()

    # Mock LLM response
    mock_response = MagicMock()
    mock_response.text = """WINNER: Progressive
KEY_ARGUMENTS:
- Progressive: Universal healthcare saves lives
- Conservative: Market competition lowers costs
COMMON_GROUND:
- Both agree costs are too high
TAKEAWAYS:
- Implement hybrid model
CONFIDENCE: 0.9
SUMMARY: A robust debate where the Progressive side presented stronger evidence for access."""
    synthesizer.client.models.generate_content.return_value = mock_response

    history = [
        DebateMessage(
            from_agent="Conservative",
            role="Debater",
            content="Markets work best",
            type=MessageType.ARGUMENT,
        ),
        DebateMessage(
            from_agent="Progressive",
            role="Debater",
            content="People need care",
            type=MessageType.ARGUMENT,
        ),
    ]

    result = await synthesizer.synthesize_debate(history, "Healthcare")

    assert result["topic"] == "Healthcare"
    assert result["winner"] == "Progressive"
    assert len(result["key_arguments"]) == 2
    assert "costs are too high" in result["common_ground"][0]
    assert result["confidence"] == 0.9
    assert "robust debate" in result["summary"]


@pytest.mark.asyncio
async def test_synthesis_parsing():
    """Test parsing of synthesis responses."""
    synthesizer = SynthesizerAgent()

    response = """WINNER: Draw
KEY_ARGUMENTS:
- A: Point 1
- B: Point 2
COMMON_GROUND:
- Agreement 1
TAKEAWAYS:
- Action 1
CONFIDENCE: 0.8
SUMMARY: Balanced discussion."""

    parsed = synthesizer._parse_synthesis_response(response)

    assert parsed["winner"] == "Draw"
    assert len(parsed["key_arguments"]) == 2
    assert parsed["common_ground"] == ["Agreement 1"]
    assert parsed["takeaways"] == ["Action 1"]
    assert parsed["confidence"] == 0.8


@pytest.mark.asyncio
async def test_synthesis_parsing_multiline_summary():
    """Test parsing synthesis with multiline summary."""
    synthesizer = SynthesizerAgent()

    response = """WINNER: Progressive
KEY_ARGUMENTS:
- Progressive: Strong point
- Conservative: Valid concern
COMMON_GROUND:
- Both care about outcomes
TAKEAWAYS:
- Find middle ground
CONFIDENCE: 0.75
SUMMARY: This was a detailed debate.
Additional summary line here.
And another line."""

    parsed = synthesizer._parse_synthesis_response(response)

    assert parsed["winner"] == "Progressive"
    assert "detailed debate" in parsed["summary"]
    assert "Additional summary" in parsed["summary"]
    assert parsed["confidence"] == 0.75


@pytest.mark.asyncio
async def test_synthesis_parsing_with_asterisks():
    """Test parsing synthesis with asterisk bullet points."""
    synthesizer = SynthesizerAgent()

    response = """WINNER: Draw
KEY_ARGUMENTS:
* Side A: First point
* Side B: Counter point
COMMON_GROUND:
* Shared value 1
* Shared value 2
TAKEAWAYS:
* Action item 1
CONFIDENCE: 0.65
SUMMARY: Balanced."""

    parsed = synthesizer._parse_synthesis_response(response)

    assert len(parsed["key_arguments"]) == 2
    assert len(parsed["common_ground"]) == 2
    assert len(parsed["takeaways"]) == 1


@pytest.mark.asyncio
async def test_synthesis_parsing_invalid_confidence():
    """Test parsing synthesis with invalid confidence score."""
    synthesizer = SynthesizerAgent()

    response = """WINNER: Progressive
KEY_ARGUMENTS:
- Point 1
COMMON_GROUND:
- Agreement
TAKEAWAYS:
- Action
CONFIDENCE: invalid
SUMMARY: Test."""

    parsed = synthesizer._parse_synthesis_response(response)

    # Should use default confidence of 0.5
    assert parsed["confidence"] == 0.5


@pytest.mark.asyncio
async def test_synthesis_parsing_out_of_range_confidence():
    """Test parsing synthesis with out of range confidence score."""
    synthesizer = SynthesizerAgent()

    # Test confidence > 1.0
    response1 = """WINNER: Draw
CONFIDENCE: 1.5
SUMMARY: Test."""

    parsed1 = synthesizer._parse_synthesis_response(response1)
    assert parsed1["confidence"] == 1.0  # Clamped to 1.0

    # Test confidence < 0.0
    response2 = """WINNER: Draw
CONFIDENCE: -0.5
SUMMARY: Test."""

    parsed2 = synthesizer._parse_synthesis_response(response2)
    assert parsed2["confidence"] == 0.0  # Clamped to 0.0


@pytest.mark.asyncio
async def test_process_message(mock_genai_client):
    """Test processing a message (synthesizer observes)."""
    synthesizer = SynthesizerAgent()

    message = {
        "from_agent": "Conservative",
        "content": "Test argument",
        "type": "ARGUMENT",
    }

    result = await synthesizer.process_message(message)

    assert result["type"] == "SYSTEM"
    assert "observing" in result["content"].lower()
    assert result["to_agent"] is None

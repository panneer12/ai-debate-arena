"""Test Synthesizer Agent."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from agents.synthesis.synthesizer import SynthesizerAgent
from protocols.message_format import DebateMessage, MessageType

@pytest.fixture
def mock_genai_client():
    with patch('google.genai.Client') as mock:
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
        DebateMessage(from_agent="Conservative", role="Debater", content="Markets work best", type=MessageType.ARGUMENT),
        DebateMessage(from_agent="Progressive", role="Debater", content="People need care", type=MessageType.ARGUMENT)
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

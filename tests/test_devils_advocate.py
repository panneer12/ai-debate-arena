"""Test Devil's Advocate Agent."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from agents.evidence.devils_advocate import DevilsAdvocateAgent

@pytest.fixture
def mock_genai_client():
    with patch('google.genai.Client') as mock:
        yield mock

@pytest.mark.asyncio
async def test_devils_advocate_initialization(mock_genai_client):
    """Test that Devil's Advocate initializes correctly."""
    advocate = DevilsAdvocateAgent()
    assert advocate.name == "Devil's Advocate"
    assert advocate.role == "Critical Challenger"
    assert len(advocate.challenge_types) == 5

@pytest.mark.asyncio
async def test_challenge_argument(mock_genai_client):
    """Test challenging an argument."""
    advocate = DevilsAdvocateAgent()
    
    # Mock LLM response
    mock_response = MagicMock()
    mock_response.text = """CHALLENGE TYPE: assumption
QUESTION: What evidence supports the claim that free markets always lead to optimal outcomes?
REASONING: This assumes perfect information and rational actors, which rarely exist in reality."""
    advocate.client.models.generate_content.return_value = mock_response
    
    result = await advocate.challenge_argument(
        "Free markets solve all problems",
        "Conservative"
    )
    
    assert result["argument"] == "Free markets solve all problems"
    assert result["author"] == "Conservative"
    assert result["challenge_type"] == "assumption"
    assert "evidence" in result["question"].lower()
    assert "reasoning" in result

@pytest.mark.asyncio
async def test_challenge_parsing():
    """Test parsing of challenge responses."""
    advocate = DevilsAdvocateAgent()
    
    response = """CHALLENGE TYPE: logical_consistency
QUESTION: How do you reconcile A with B?
REASONING: These statements appear contradictory."""
    
    challenge_type, question, reasoning = advocate._parse_challenge_response(response)
    
    assert challenge_type == "logical_consistency"
    assert "reconcile" in question
    assert "contradictory" in reasoning

@pytest.mark.asyncio
async def test_process_message(mock_genai_client):
    """Test processing a debate message."""
    advocate = DevilsAdvocateAgent()
    
    # Mock LLM response
    mock_response = MagicMock()
    mock_response.text = """CHALLENGE TYPE: counterexample
QUESTION: What about countries where this failed?
REASONING: Historical evidence contradicts this claim."""
    advocate.client.models.generate_content.return_value = mock_response
    
    message = {
        "from_agent": "Progressive",
        "content": "This policy always works",
        "type": "ARGUMENT"
    }
    
    result = await advocate.process_message(message)
    
    assert result["type"] == "QUESTION"
    assert result["to_agent"] == "Progressive"
    assert "Devil's Advocate" in result["content"]
    assert "counterexample" in result["content"].lower()

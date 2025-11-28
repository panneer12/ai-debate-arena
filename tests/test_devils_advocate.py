"""Test Devil's Advocate Agent."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.evidence.devils_advocate import DevilsAdvocateAgent


@pytest.fixture
def mock_genai_client():
    with patch("google.genai.Client") as mock:
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

    result = await advocate.challenge_argument("Free markets solve all problems", "Conservative")

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
        "type": "ARGUMENT",
    }

    result = await advocate.process_message(message)

    assert result["type"] == "QUESTION"
    assert result["to_agent"] == "Progressive"
    assert "Devil's Advocate" in result["content"]
    assert "counterexample" in result["content"].lower()


@pytest.mark.asyncio
async def test_challenge_parsing_alternative_explanation():
    """Test parsing alternative_explanation challenge type."""
    advocate = DevilsAdvocateAgent()

    response = """CHALLENGE TYPE: alternative_explanation
QUESTION: Could this be due to other factors?
REASONING: Correlation doesn't imply causation."""

    challenge_type, question, reasoning = advocate._parse_challenge_response(response)

    assert challenge_type == "alternative_explanation"
    assert "other factors" in question
    assert "causation" in reasoning


@pytest.mark.asyncio
async def test_challenge_parsing_unintended_consequence():
    """Test parsing unintended_consequence challenge type."""
    advocate = DevilsAdvocateAgent()

    response = """CHALLENGE TYPE: unintended_consequence
QUESTION: What about the negative side effects?
REASONING: Every action has reactions."""

    challenge_type, question, reasoning = advocate._parse_challenge_response(response)

    assert challenge_type == "unintended_consequence"
    assert "side effects" in question


@pytest.mark.asyncio
async def test_challenge_parsing_no_structured_format():
    """Test parsing response without structured format (fallback)."""
    advocate = DevilsAdvocateAgent()

    # LLM didn't follow format
    response = "What makes you so sure about that assumption?"

    challenge_type, question, reasoning = advocate._parse_challenge_response(response)

    # Should default to 'assumption' and use full response as question
    assert challenge_type == "assumption"
    assert question == response
    assert reasoning == ""


@pytest.mark.asyncio
async def test_challenge_parsing_missing_question_field():
    """Test parsing when QUESTION field is missing."""
    advocate = DevilsAdvocateAgent()

    response = """CHALLENGE TYPE: logical_consistency
REASONING: These two claims contradict each other."""

    challenge_type, question, reasoning = advocate._parse_challenge_response(response)

    assert challenge_type == "logical_consistency"
    # Should use full response as question when QUESTION field missing
    assert "CHALLENGE TYPE" in question
    assert reasoning == "These two claims contradict each other."


@pytest.mark.asyncio
async def test_challenge_all_types(mock_genai_client):
    """Test that all challenge types are recognized."""
    advocate = DevilsAdvocateAgent()

    for challenge_type in advocate.challenge_types:
        mock_response = MagicMock()
        mock_response.text = f"""CHALLENGE TYPE: {challenge_type}
QUESTION: Test question for {challenge_type}?
REASONING: Test reasoning."""
        advocate.client.models.generate_content.return_value = mock_response

        result = await advocate.challenge_argument(
            f"Test argument for {challenge_type}", "TestAgent"
        )

        assert result["challenge_type"] == challenge_type
        assert challenge_type in result["question"]


@pytest.mark.asyncio
async def test_process_message_formatting(mock_genai_client):
    """Test that process_message formats output correctly."""
    advocate = DevilsAdvocateAgent()

    mock_response = MagicMock()
    mock_response.text = """CHALLENGE TYPE: assumption
QUESTION: What evidence supports this assumption?
REASONING: Assumptions need verification."""
    advocate.client.models.generate_content.return_value = mock_response

    message = {
        "from_agent": "Conservative",
        "content": "Markets always self-correct",
        "type": "ARGUMENT",
    }

    result = await advocate.process_message(message)

    # Check formatting
    assert "To: Conservative" in result["content"]
    assert "Type: Assumption" in result["content"]  # Should be title-cased
    assert "Why this matters:" in result["content"]
    assert "Assumptions need verification" in result["content"]

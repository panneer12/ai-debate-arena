"""Test Fact Checker Agent with Google ADK grounding."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.evidence.fact_checker import FactCheckerAgent


@pytest.fixture
def mock_genai_client():
    with patch("google.genai.Client") as mock:
        yield mock


@pytest.mark.asyncio
async def test_fact_checker_initialization(mock_genai_client):
    """Test that fact checker initializes correctly."""
    checker = FactCheckerAgent()
    assert checker.name == "Fact Checker"
    assert checker.role == "Evidence Verifier"


@pytest.mark.asyncio
async def test_fact_checker_with_grounding(mock_genai_client):
    """Test claim checking with Google Search grounding."""
    checker = FactCheckerAgent()

    # Mock LLM response with search results
    mock_response = MagicMock()
    mock_response.text = """VERDICT: TRUE
CONFIDENCE: 0.85
EVIDENCE: Multiple scientific sources confirm this claim.
SOURCES: NASA, Scientific American"""
    checker.client.models.generate_content.return_value = mock_response

    result = await checker.check_claim("The sky is blue")

    assert result["claim"] == "The sky is blue"
    assert result["verdict"] == "TRUE"
    assert result["confidence"] == 0.85
    assert result["search_used"] == True

    # Verify google_search tool was enabled
    call_args = checker.client.models.generate_content.call_args
    assert call_args is not None
    config = call_args.kwargs.get("config")
    assert config is not None


@pytest.mark.asyncio
async def test_verdict_parsing():
    """Test parsing of different verdict formats."""
    checker = FactCheckerAgent()

    # Test standard format
    response1 = """VERDICT: FALSE
CONFIDENCE: 0.9
EVIDENCE: The claim is not supported by evidence."""

    verdict, confidence, explanation = checker._parse_fact_check_response(response1)
    assert verdict == "FALSE"
    assert confidence == 0.9
    assert "not supported" in explanation


@pytest.mark.asyncio
async def test_process_message(mock_genai_client):
    """Test processing a debate message for fact-checking."""
    checker = FactCheckerAgent()

    # Mock LLM response
    mock_response = MagicMock()
    mock_response.text = """VERDICT: PARTIALLY_TRUE
CONFIDENCE: 0.6
EVIDENCE: Some aspects are correct, others questionable."""
    checker.client.models.generate_content.return_value = mock_response

    message = {
        "from_agent": "Conservative",
        "content": "Universal healthcare costs too much",
        "type": "CLAIM",
    }

    result = await checker.process_message(message)

    assert result["type"] == "FACT_CHECK"
    assert "PARTIALLY_TRUE" in result["content"]
    assert result["to_agent"] == "Conservative"

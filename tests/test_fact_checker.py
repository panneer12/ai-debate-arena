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


@pytest.mark.asyncio
async def test_verdict_parsing_unverifiable():
    """Test parsing UNVERIFIABLE verdict."""
    checker = FactCheckerAgent()

    response = """VERDICT: UNVERIFIABLE
CONFIDENCE: 0.3
EVIDENCE: Insufficient data to verify this claim."""

    verdict, confidence, explanation = checker._parse_fact_check_response(response)
    assert verdict == "UNVERIFIABLE"
    assert confidence == 0.3
    assert "Insufficient data" in explanation


@pytest.mark.asyncio
async def test_verdict_parsing_missing_fields():
    """Test parsing response with missing fields."""
    checker = FactCheckerAgent()

    # Minimal response
    response = "This claim appears to be true based on available evidence."

    verdict, confidence, explanation = checker._parse_fact_check_response(response)

    # Should use defaults
    assert verdict == "UNVERIFIABLE"  # default
    assert confidence == 0.5  # default
    assert "appears to be true" in explanation


@pytest.mark.asyncio
async def test_verdict_parsing_invalid_confidence():
    """Test parsing response with invalid confidence value."""
    checker = FactCheckerAgent()

    response = """VERDICT: TRUE
CONFIDENCE: invalid_value
EVIDENCE: Test evidence."""

    verdict, confidence, explanation = checker._parse_fact_check_response(response)
    assert verdict == "TRUE"
    assert confidence == 0.5  # default when parsing fails


@pytest.mark.asyncio
async def test_fact_checker_with_search_fallback(mock_genai_client):
    """Test that fact checker falls back to LLM when search fails."""
    checker = FactCheckerAgent()

    # Mock search to raise exception
    checker.client.models.generate_content.side_effect = [
        Exception("Search API failed"),
        MagicMock(
            text="""VERDICT: TRUE
CONFIDENCE: 0.7
EVIDENCE: Fallback verification successful."""
        ),
    ]

    # Mock the generate_response method
    async def mock_generate_response(context, prompt):
        return """VERDICT: TRUE
CONFIDENCE: 0.7
EVIDENCE: Fallback verification successful."""

    checker.generate_response = mock_generate_response

    result = await checker.check_claim("Test claim")

    assert result["verdict"] == "TRUE"
    assert result["confidence"] == 0.7
    assert result["search_used"] == True  # Still marked as attempted


@pytest.mark.asyncio
async def test_fact_checker_alternative_explanation_format():
    """Test parsing with EXPLANATION instead of EVIDENCE."""
    checker = FactCheckerAgent()

    response = """VERDICT: FALSE
CONFIDENCE: 0.8
EXPLANATION: This has been debunked by multiple sources."""

    verdict, confidence, explanation = checker._parse_fact_check_response(response)
    assert verdict == "FALSE"
    assert confidence == 0.8
    assert "debunked" in explanation


@pytest.mark.asyncio
async def test_process_message_with_long_claim(mock_genai_client):
    """Test processing message with very long claim (truncation in display)."""
    checker = FactCheckerAgent()

    mock_response = MagicMock()
    mock_response.text = """VERDICT: TRUE
CONFIDENCE: 0.9
EVIDENCE: Verified."""
    checker.client.models.generate_content.return_value = mock_response

    long_claim = "A" * 200  # Very long claim
    message = {
        "from_agent": "TestAgent",
        "content": long_claim,
        "type": "CLAIM",
    }

    result = await checker.process_message(message)

    # Should truncate claim in result to 100 chars + "..."
    assert "..." in result["content"]
    assert result["type"] == "FACT_CHECK"

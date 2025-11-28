"""Test Argument Analyzer Agent."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.synthesis.analyzer import ArgumentAnalyzerAgent


@pytest.fixture
def mock_genai_client():
    with patch("google.genai.Client") as mock:
        yield mock


@pytest.mark.asyncio
async def test_analyzer_initialization(mock_genai_client):
    """Test that analyzer initializes correctly."""
    analyzer = ArgumentAnalyzerAgent()
    assert analyzer.name == "Argument Analyzer"
    assert analyzer.role == "Logic Evaluator"
    assert len(analyzer.fallacy_types) == 8


@pytest.mark.asyncio
async def test_analyze_argument(mock_genai_client):
    """Test analyzing an argument."""
    analyzer = ArgumentAnalyzerAgent()

    # Mock LLM response
    mock_response = MagicMock()
    mock_response.text = """LOGICAL_VALIDITY: 0.7
EVIDENCE_QUALITY: 0.6
FALLACIES: none
STRENGTHS: Clear reasoning, supported by data
WEAKNESSES: Could use more recent examples"""
    analyzer.client.models.generate_content.return_value = mock_response

    result = await analyzer.analyze_argument(
        "Markets are efficient because competition drives innovation", "Conservative"
    )

    assert result["author"] == "Conservative"
    assert result["logical_validity"] == 0.7
    assert result["evidence_quality"] == 0.6
    assert result["fallacies"] == []
    assert "reasoning" in result["strengths"].lower()


@pytest.mark.asyncio
async def test_fallacy_detection(mock_genai_client):
    """Test detecting logical fallacies."""
    analyzer = ArgumentAnalyzerAgent()

    # Mock response with fallacies
    mock_response = MagicMock()
    mock_response.text = """LOGICAL_VALIDITY: 0.3
EVIDENCE_QUALITY: 0.4
FALLACIES: ad_hominem, straw_man
STRENGTHS: Passionate delivery
WEAKNESSES: Attacks person not argument, misrepresents position"""
    analyzer.client.models.generate_content.return_value = mock_response

    result = await analyzer.analyze_argument("You're wrong because you're biased", "TestAgent")

    assert len(result["fallacies"]) == 2
    assert "ad_hominem" in result["fallacies"]
    assert "straw_man" in result["fallacies"]
    assert result["logical_validity"] < 0.5


@pytest.mark.asyncio
async def test_analysis_parsing():
    """Test parsing of analysis responses."""
    analyzer = ArgumentAnalyzerAgent()

    response = """LOGICAL_VALIDITY: 0.9
EVIDENCE_QUALITY: 0.85
FALLACIES: none
STRENGTHS: Strong evidence, clear logic
WEAKNESSES: Could address counterarguments"""

    parsed = analyzer._parse_analysis_response(response)

    assert parsed["logical_validity"] == 0.9
    assert parsed["evidence_quality"] == 0.85
    assert parsed["fallacies"] == []
    assert "evidence" in parsed["strengths"].lower()


@pytest.mark.asyncio
async def test_process_message(mock_genai_client):
    """Test processing a debate message."""
    analyzer = ArgumentAnalyzerAgent()

    # Mock LLM response
    mock_response = MagicMock()
    mock_response.text = """LOGICAL_VALIDITY: 0.6
EVIDENCE_QUALITY: 0.7
FALLACIES: appeal_to_authority
STRENGTHS: Cites experts
WEAKNESSES: Relies too heavily on single source"""
    analyzer.client.models.generate_content.return_value = mock_response

    message = {
        "from_agent": "Progressive",
        "content": "Experts say this is the best approach",
        "type": "ARGUMENT",
    }

    result = await analyzer.process_message(message)

    assert result["type"] == "SYSTEM"
    assert "Progressive" in result["content"]
    assert "60%" in result["content"] or "0.6" in result["content"]
    assert "appeal_to_authority" in result["content"].lower()


@pytest.mark.asyncio
async def test_analysis_parsing_alternative_field_names():
    """Test parsing with alternative field names."""
    analyzer = ArgumentAnalyzerAgent()

    response = """LOGICAL STRUCTURE: 0.75
EVIDENCE QUALITY: 0.8
FALLACY: circular_reasoning
STRENGTH: Well-structured
WEAKNESS: Assumes conclusion"""

    parsed = analyzer._parse_analysis_response(response)

    assert parsed["logical_validity"] == 0.75
    assert parsed["evidence_quality"] == 0.8
    assert "circular_reasoning" in parsed["fallacies"]
    assert "structured" in parsed["strengths"].lower()


@pytest.mark.asyncio
async def test_analysis_parsing_no_fallacies():
    """Test parsing when fallacies field says 'none'."""
    analyzer = ArgumentAnalyzerAgent()

    response = """LOGICAL_VALIDITY: 0.9
EVIDENCE_QUALITY: 0.85
FALLACIES: none detected
STRENGTHS: Strong evidence
WEAKNESSES: Minor gaps"""

    parsed = analyzer._parse_analysis_response(response)

    assert parsed["fallacies"] == []


@pytest.mark.asyncio
async def test_analysis_parsing_invalid_scores():
    """Test parsing with invalid scores."""
    analyzer = ArgumentAnalyzerAgent()

    response = """LOGICAL_VALIDITY: invalid
EVIDENCE_QUALITY: bad_value
FALLACIES: none
STRENGTHS: Test
WEAKNESSES: Test"""

    parsed = analyzer._parse_analysis_response(response)

    # Should use defaults
    assert parsed["logical_validity"] == 0.5
    assert parsed["evidence_quality"] == 0.5


@pytest.mark.asyncio
async def test_analysis_parsing_out_of_range_scores():
    """Test parsing with out of range scores."""
    analyzer = ArgumentAnalyzerAgent()

    response = """LOGICAL_VALIDITY: 1.5
EVIDENCE_QUALITY: -0.3
FALLACIES: none
STRENGTHS: Test
WEAKNESSES: Test"""

    parsed = analyzer._parse_analysis_response(response)

    # Should clamp to valid range
    assert parsed["logical_validity"] == 1.0
    assert parsed["evidence_quality"] == 0.0


@pytest.mark.asyncio
async def test_process_message_no_fallacies(mock_genai_client):
    """Test processing message with no fallacies detected."""
    analyzer = ArgumentAnalyzerAgent()

    mock_response = MagicMock()
    mock_response.text = """LOGICAL_VALIDITY: 0.9
EVIDENCE_QUALITY: 0.85
FALLACIES: none
STRENGTHS: Clear logic, strong evidence
WEAKNESSES: Could be more concise"""
    analyzer.client.models.generate_content.return_value = mock_response

    message = {
        "from_agent": "Conservative",
        "content": "Well-reasoned argument with citations",
        "type": "ARGUMENT",
    }

    result = await analyzer.process_message(message)

    assert "None detected" in result["content"]

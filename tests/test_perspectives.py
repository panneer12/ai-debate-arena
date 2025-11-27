"""Test Perspective Agents."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agents.perspectives.conservative import ConservativeAgent
from agents.perspectives.progressive import ProgressiveAgent


@pytest.fixture
def mock_genai_client():
    with patch("google.genai.Client") as mock:
        yield mock


@pytest.mark.asyncio
async def test_conservative_worldview_injection(mock_genai_client):
    agent = ConservativeAgent()

    # Mock response
    mock_response = MagicMock()
    mock_response.text = "Response"
    agent.client.models.generate_content.return_value = mock_response

    await agent.generate_response("Context", "Prompt")

    # Check if worldview was injected in the call
    call_args = agent.client.models.generate_content.call_args
    assert call_args is not None
    prompt_sent = call_args.kwargs["contents"]

    assert "Conservative debater" in prompt_sent
    assert "Free market capitalism" in prompt_sent
    assert "Traditional values" in prompt_sent


@pytest.mark.asyncio
async def test_progressive_worldview_injection(mock_genai_client):
    agent = ProgressiveAgent()

    # Mock response
    mock_response = MagicMock()
    mock_response.text = "Response"
    agent.client.models.generate_content.return_value = mock_response

    await agent.generate_response("Context", "Prompt")

    # Check if worldview was injected in the call
    call_args = agent.client.models.generate_content.call_args
    assert call_args is not None
    prompt_sent = call_args.kwargs["contents"]

    assert "Progressive debater" in prompt_sent
    assert "Regulated markets" in prompt_sent
    assert "Social justice" in prompt_sent


@pytest.mark.asyncio
async def test_conservative_process_message(mock_genai_client):
    """Test that process_message returns a valid DebateMessage dict."""
    agent = ConservativeAgent()

    # Mock response
    mock_response = MagicMock()
    mock_response.text = "I strongly disagree with that position."
    agent.client.models.generate_content.return_value = mock_response

    # Simulate incoming message
    incoming_message = {
        "from_agent": "Moderator",
        "role": "Moderator",
        "content": "What is your stance on healthcare?",
        "type": "QUESTION",
    }

    result = await agent.process_message(incoming_message)

    # Verify result is a valid dict with required fields
    assert isinstance(result, dict)
    assert "content" in result
    assert "from_agent" in result
    assert "type" in result
    assert "role" in result
    assert "timestamp" in result

    # Verify values
    assert result["from_agent"] == "Conservative"
    assert result["role"] == "Debater"
    assert result["content"] == "I strongly disagree with that position."
    assert result["type"] is not None  # Should be MessageType.ARGUMENT


@pytest.mark.asyncio
async def test_progressive_process_message(mock_genai_client):
    """Test that process_message returns a valid DebateMessage dict."""
    agent = ProgressiveAgent()

    # Mock response
    mock_response = MagicMock()
    mock_response.text = "We need systemic change to address this."
    agent.client.models.generate_content.return_value = mock_response

    # Simulate incoming message
    incoming_message = {
        "from_agent": "Conservative",
        "role": "Debater",
        "content": "Free markets solve everything.",
        "type": "ARGUMENT",
    }

    result = await agent.process_message(incoming_message)

    # Verify result is a valid dict with required fields
    assert isinstance(result, dict)
    assert "content" in result
    assert "from_agent" in result
    assert "type" in result
    assert "role" in result
    assert "timestamp" in result

    # Verify values
    assert result["from_agent"] == "Progressive"
    assert result["role"] == "Debater"
    assert result["content"] == "We need systemic change to address this."


@pytest.mark.asyncio
async def test_process_message_creates_valid_debate_message(mock_genai_client):
    """Test that process_message output can be used to create a DebateMessage."""
    from protocols.message_format import DebateMessage

    agent = ConservativeAgent()

    # Mock response
    mock_response = MagicMock()
    mock_response.text = "Test response"
    agent.client.models.generate_content.return_value = mock_response

    incoming_message = {"from_agent": "Moderator", "content": "Test question", "type": "QUESTION"}

    result = await agent.process_message(incoming_message)

    # This should NOT raise a ValidationError
    try:
        msg = DebateMessage(**result)
        assert msg.from_agent == "Conservative"
        assert msg.content == "Test response"
    except Exception as e:
        pytest.fail(f"Failed to create DebateMessage from process_message result: {e}")

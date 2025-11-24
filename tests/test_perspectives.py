"""Test Perspective Agents."""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from agents.perspectives.conservative import ConservativeAgent
from agents.perspectives.progressive import ProgressiveAgent

@pytest.fixture
def mock_genai_client():
    with patch('google.genai.Client') as mock:
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
    prompt_sent = call_args.kwargs['contents']
    
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
    prompt_sent = call_args.kwargs['contents']
    
    assert "Progressive debater" in prompt_sent
    assert "Regulated markets" in prompt_sent
    assert "Social justice" in prompt_sent

"""Test base architecture components."""
import pytest
import asyncio
from unittest.mock import MagicMock, patch
from datetime import datetime

from agents.base_agent import BaseDebateAgent
from protocols.message_format import DebateMessage, MessageType
from protocols.debate_protocol import DebateProtocol, DebatePhase

# Concrete implementation for testing abstract base class
class TestAgent(BaseDebateAgent):
    async def process_message(self, message):
        return {"type": "ACK", "content": "Received"}

@pytest.fixture
def mock_genai_client():
    with patch('google.genai.Client') as mock:
        yield mock

@pytest.mark.asyncio
async def test_agent_initialization(mock_genai_client):
    """Test that agent initializes correctly."""
    agent = TestAgent("TestBot", "Tester")
    assert agent.name == "TestBot"
    assert agent.role == "Tester"
    assert agent.id is not None
    assert agent.client is not None

@pytest.mark.asyncio
async def test_message_creation():
    """Test message format validation."""
    msg = DebateMessage(
        type=MessageType.CLAIM,
        from_agent="Agent A",
        content="Sky is blue"
    )
    assert msg.type == MessageType.CLAIM
    assert msg.content == "Sky is blue"
    assert msg.timestamp is not None
    assert isinstance(msg.to_dict(), dict)

def test_debate_protocol():
    """Test debate phase transitions."""
    protocol = DebateProtocol()
    
    # Check initial config
    opening = protocol.get_phase_config(DebatePhase.OPENING_STATEMENTS)
    assert opening.name == DebatePhase.OPENING_STATEMENTS
    assert opening.duration_seconds > 0
    
    # Check transitions
    next_phase = protocol.get_next_phase(DebatePhase.OPENING_STATEMENTS)
    assert next_phase == DebatePhase.FIRST_REBUTTALS
    
    last_phase = protocol.get_next_phase(DebatePhase.SYNTHESIS)
    assert last_phase == DebatePhase.COMPLETE

@pytest.mark.asyncio
async def test_agent_response_generation(mock_genai_client):
    """Test LLM response generation wrapper."""
    agent = TestAgent("TestBot", "Tester")
    
    # Mock the generate_content response
    mock_response = MagicMock()
    mock_response.text = "Mocked response"
    agent.client.models.generate_content.return_value = mock_response
    
    response = await agent.generate_response("Context", "Prompt")
    assert response == "Mocked response"

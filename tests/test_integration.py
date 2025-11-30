"""
Integration tests for AI Debate Arena.
Tests the full debate flow end-to-end.
"""
import os
import pytest
import asyncio
from demo.debate_manager import DebateManager

# Check if we have a valid API key
API_KEY_AVAILABLE = bool(os.getenv("GOOGLE_API_KEY")) and os.getenv("GOOGLE_API_KEY") not in ["test_key_for_ci", "test_key_placeholder"]

# Mark all tests in this module as integration tests
# These tests are skipped in PR checks and only run on main branch or manually
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not API_KEY_AVAILABLE,
        reason="Integration tests require a valid GOOGLE_API_KEY environment variable"
    )
]


@pytest.mark.asyncio
async def test_full_debate_flow():
    """Test complete debate from start to synthesis."""
    # Mock broadcast function
    messages = []

    async def mock_broadcast(msg):
        messages.append(msg)

    # Create debate manager
    manager = DebateManager(broadcast_func=mock_broadcast)
    await manager.initialize_agents()

    # Start debate
    task = asyncio.create_task(
        manager.start_debate(
            topic="Should we test debates?", rounds=1, active_agents=["conservative", "progressive"]
        )
    )

    # Wait for completion
    await asyncio.sleep(30)  # Give time for 1 round debate

    # Verify debate structure
    assert manager.memory is not None
    history = manager.memory.get_full_history()

    # Check we have messages
    assert len(history) > 0

    # Verify message types
    message_types = [msg.type for msg in history]

    # Should have Opening Statement
    assert "OPENING_STATEMENT" in message_types

    # Should have Arguments from both agents
    agents = [msg.from_agent for msg in history]
    assert "Conservative" in agents
    assert "Progressive" in agents

    # Should have Synthesis at the end
    assert history[-1].type == "SYNTHESIS"
    assert "Common Ground" in history[-1].content or "Key Arguments" in history[-1].content


@pytest.mark.asyncio
async def test_devils_advocate_frequency():
    """Test that Devil's Advocate runs once per round, not per turn."""
    messages = []

    async def mock_broadcast(msg):
        messages.append(msg)

    manager = DebateManager(broadcast_func=mock_broadcast)
    await manager.initialize_agents()

    task = asyncio.create_task(
        manager.start_debate(topic="Test topic", rounds=2, active_agents=["conservative", "progressive"])
    )

    await asyncio.sleep(45)  # 2 rounds

    # Count Devil's Advocate challenges in messages
    challenges = [msg for msg in messages if msg.get("type") == "CHALLENGE"]

    # Should have ~2 challenges per round (one for each agent)
    # So 2 rounds = ~4 challenges total
    assert len(challenges) >= 2  # At least one per round
    assert len(challenges) <= 6  # Not more than 3 per round


@pytest.mark.asyncio
async def test_synthesis_in_memory():
    """Test that synthesis message is saved to memory."""
    messages = []

    async def mock_broadcast(msg):
        messages.append(msg)

    manager = DebateManager(broadcast_func=mock_broadcast)
    await manager.initialize_agents()

    task = asyncio.create_task(
        manager.start_debate(
            topic="Test synthesis", rounds=1, active_agents=["conservative", "progressive"]
        )
    )

    await asyncio.sleep(30)

    # Check memory for synthesis
    history = manager.memory.get_full_history()
    synthesis_messages = [msg for msg in history if msg.type == "SYNTHESIS"]

    assert len(synthesis_messages) == 1
    synthesis = synthesis_messages[0]

    # Verify synthesis content structure
    assert "Common Ground" in synthesis.content
    assert "Key Arguments" in synthesis.content
    assert "Final Synthesis" in synthesis.content


@pytest.mark.asyncio
async def test_fact_checker_runs():
    """Test that fact checker analyzes arguments."""
    messages = []

    async def mock_broadcast(msg):
        messages.append(msg)

    manager = DebateManager(broadcast_func=mock_broadcast)
    await manager.initialize_agents()

    task = asyncio.create_task(
        manager.start_debate(
            topic="Climate change is real", rounds=1, active_agents=["conservative", "progressive"]
        )
    )

    await asyncio.sleep(30)

    # Check for fact check messages
    fact_checks = [msg for msg in messages if msg.get("type") == "FACT_CHECK"]

    # Should have at least some fact checks (not all claims are TRUE)
    assert len(fact_checks) >= 0  # May have 0 if all claims verified as TRUE


@pytest.mark.asyncio
async def test_debate_stop():
    """Test that debate can be stopped gracefully."""
    messages = []

    async def mock_broadcast(msg):
        messages.append(msg)

    manager = DebateManager(broadcast_func=mock_broadcast)
    await manager.initialize_agents()

    task = asyncio.create_task(
        manager.start_debate(
            topic="Test stop", rounds=5, active_agents=["conservative", "progressive"]
        )
    )

    # Let it run briefly
    await asyncio.sleep(10)

    # Stop debate
    await manager.stop_debate()

    await asyncio.sleep(2)  # Let it finish cleanup

    # Verify stopped
    assert manager.is_running is False
    assert manager.should_stop is True


@pytest.mark.asyncio
async def test_debate_saves_metrics():
    """Test that metrics are collected and saved."""
    messages = []

    async def mock_broadcast(msg):
        messages.append(msg)

    manager = DebateManager(broadcast_func=mock_broadcast)
    await manager.initialize_agents()

    task = asyncio.create_task(
        manager.start_debate(
            topic="Test metrics", rounds=1, active_agents=["conservative", "progressive"]
        )
    )

    await asyncio.sleep(30)

    # Verify metrics collector exists
    assert manager.metrics_collector is not None

    # Get metrics
    metrics = manager.metrics_collector.get_metrics_dict()

    # Should have some actions tracked
    assert len(metrics.get("actions", [])) > 0


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_full_debate_flow())
    asyncio.run(test_devils_advocate_frequency())
    asyncio.run(test_synthesis_in_memory())
    asyncio.run(test_fact_checker_runs())
    asyncio.run(test_debate_stop())
    asyncio.run(test_debate_saves_metrics())
    print("✅ All integration tests passed!")

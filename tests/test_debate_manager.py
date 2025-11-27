"""
Test suite for DebateManager class.

Tests debate lifecycle, message broadcasting, round progression,
agent turn handling, analysis phase, synthesis phase, and memory integration.

NOTE: These are INTEGRATION TESTS that make real API calls to LLM services.
They are slow (2+ minutes) and cost money. Run them:
- Manually before releases
- On a schedule (nightly)
- NOT on every commit

Run with: pytest -m integration
"""

import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
import pytest_asyncio

from demo.debate_manager import DebateManager

# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration
from memory.memory_bank import MemoryBank
from protocols.message_format import DebateMessage, MessageType


class TestDebateManagerLifecycle:
    """Test debate lifecycle management."""

    @pytest.fixture
    def mock_broadcast(self):
        """Create a mock broadcast function."""
        return AsyncMock()

    @pytest_asyncio.fixture
    async def debate_manager(self, mock_broadcast):
        """Create a DebateManager instance."""
        manager = DebateManager(mock_broadcast)
        await manager.initialize_agents()
        return manager

    @pytest.mark.asyncio
    async def test_initialize_agents(self, debate_manager):
        """Test that all agents are initialized correctly."""
        assert debate_manager.moderator is not None
        assert debate_manager.conservative is not None
        assert debate_manager.progressive is not None
        assert debate_manager.fact_checker is not None
        assert debate_manager.devils_advocate is not None
        assert debate_manager.analyzer is not None
        assert debate_manager.synthesizer is not None
        assert debate_manager.common_ground is not None

    @pytest.mark.asyncio
    async def test_start_debate(self, debate_manager, mock_broadcast):
        """Test starting a debate."""
        with patch.object(debate_manager, "_run_debate_wrapper", new_callable=AsyncMock):
            await debate_manager.start_debate("Test topic", rounds=1)

            assert debate_manager.is_running is True
            assert debate_manager.should_stop is False
            assert debate_manager.memory is not None
            assert debate_manager.debate_id is not None
            assert debate_manager.metrics_collector is not None

    @pytest.mark.asyncio
    async def test_start_debate_while_running(self, debate_manager, mock_broadcast):
        """Test that starting a debate while one is running does nothing."""
        debate_manager.is_running = True

        with patch.object(
            debate_manager, "_run_debate_wrapper", new_callable=AsyncMock
        ) as mock_run:
            await debate_manager.start_debate("Test topic", rounds=1)

            # Should not start a new debate
            mock_run.assert_not_called()

    @pytest.mark.asyncio
    async def test_stop_debate(self, debate_manager):
        """Test stopping a debate."""
        debate_manager.is_running = True
        debate_manager.should_stop = False

        await debate_manager.stop_debate()

        assert debate_manager.should_stop is True
        assert debate_manager.is_running is False

    @pytest.mark.asyncio
    async def test_debate_without_initialized_agents(self, mock_broadcast):
        """Test that starting debate without initialized agents raises error."""
        manager = DebateManager(mock_broadcast)
        # Don't initialize agents

        manager.memory = MagicMock()
        manager.metrics_collector = MagicMock()

        with pytest.raises(RuntimeError, match="Agents must be initialized"):
            with patch.object(manager, "_run_debate_wrapper", new_callable=AsyncMock):
                await manager.start_debate("Test topic", rounds=1)


class TestMessageBroadcasting:
    """Test message broadcasting functionality."""

    @pytest.fixture
    def mock_broadcast(self):
        """Create a mock broadcast function."""
        return AsyncMock()

    @pytest_asyncio.fixture
    async def debate_manager(self, mock_broadcast):
        """Create a DebateManager instance."""
        manager = DebateManager(mock_broadcast)
        await manager.initialize_agents()
        return manager

    @pytest.mark.asyncio
    async def test_broadcast_opening_statement(self, debate_manager, mock_broadcast):
        """Test broadcasting opening statement."""
        debate_manager.memory = MagicMock()
        debate_manager.memory.add_message = Mock()
        debate_manager.memory.save_debate = Mock(return_value="test_path")
        debate_manager.memory.debate_id = "test_123"
        debate_manager.metrics_collector = MagicMock()
        debate_manager.metrics_collector.get_metrics_dict = Mock(return_value={})

        with patch.object(
            debate_manager.moderator, "generate_response", return_value="Opening statement"
        ):
            with patch.object(debate_manager, "_run_synthesis", new_callable=AsyncMock):
                await debate_manager._run_debate_loop("Test topic", rounds=0)

        # Should broadcast status and opening
        calls = mock_broadcast.call_args_list
        status_calls = [c for c in calls if c[0][0].get("type") == "STATUS"]
        assert len(status_calls) > 0

        # Check for opening message broadcast
        opening_calls = [c for c in calls if "Opening" in str(c) or "OPENING" in str(c)]
        assert len(opening_calls) > 0

    @pytest.mark.asyncio
    async def test_broadcast_round_start(self, debate_manager, mock_broadcast):
        """Test broadcasting round start."""
        debate_manager.memory = MagicMock()
        debate_manager.memory.get_full_history = Mock(
            return_value=[
                DebateMessage(
                    from_agent="Moderator",
                    role="moderator",
                    content="Opening",
                    type=MessageType.OPENING_STATEMENT,
                )
            ]
        )
        debate_manager.memory.add_message = Mock()
        debate_manager.memory.save_debate = Mock(return_value="test_path")
        debate_manager.memory.debate_id = "test_123"
        debate_manager.metrics_collector = MagicMock()
        debate_manager.metrics_collector.get_metrics_dict = Mock(return_value={})

        with patch.object(debate_manager.moderator, "generate_response", return_value="Opening"):
            with patch.object(debate_manager, "_handle_turn", new_callable=AsyncMock):
                with patch.object(debate_manager, "_run_synthesis", new_callable=AsyncMock):
                    await debate_manager._run_debate_loop("Test topic", rounds=2)

        # Should broadcast ROUND_START for each round
        calls = mock_broadcast.call_args_list
        round_calls = [c for c in calls if c[0][0].get("type") == "ROUND_START"]
        assert len(round_calls) == 2


class TestRoundProgression:
    """Test round progression logic."""

    @pytest.fixture
    def mock_broadcast(self):
        """Create a mock broadcast function."""
        return AsyncMock()

    @pytest_asyncio.fixture
    async def debate_manager(self, mock_broadcast):
        """Create a DebateManager instance."""
        manager = DebateManager(mock_broadcast)
        await manager.initialize_agents()
        return manager

    @pytest.mark.asyncio
    async def test_multiple_rounds(self, debate_manager, mock_broadcast):
        """Test that multiple rounds are executed correctly."""
        debate_manager.memory = MagicMock()
        debate_manager.memory.get_full_history = Mock(
            return_value=[
                DebateMessage(
                    from_agent="Moderator",
                    role="moderator",
                    content="Opening",
                    type=MessageType.OPENING_STATEMENT,
                )
            ]
        )
        debate_manager.memory.add_message = Mock()
        debate_manager.memory.save_debate = Mock(return_value="test_path")
        debate_manager.memory.debate_id = "test_123"
        debate_manager.metrics_collector = MagicMock()
        debate_manager.metrics_collector.get_metrics_dict = Mock(return_value={})

        turn_counter = {"count": 0}

        async def mock_handle_turn(agent, round_num):
            turn_counter["count"] += 1

        with patch.object(debate_manager.moderator, "generate_response", return_value="Opening"):
            with patch.object(debate_manager, "_handle_turn", new=mock_handle_turn):
                with patch.object(debate_manager, "_run_synthesis", new_callable=AsyncMock):
                    await debate_manager._run_debate_loop("Test topic", rounds=3)

        # 3 rounds * 2 agents (conservative + progressive) = 6 turns
        assert turn_counter["count"] == 6

    @pytest.mark.asyncio
    async def test_early_stop_during_rounds(self, debate_manager, mock_broadcast):
        """Test that setting should_stop halts the debate."""
        debate_manager.memory = MagicMock()
        debate_manager.memory.get_full_history = Mock(
            return_value=[
                DebateMessage(
                    from_agent="Moderator",
                    role="moderator",
                    content="Opening",
                    type=MessageType.OPENING_STATEMENT,
                )
            ]
        )
        debate_manager.memory.add_message = Mock()
        debate_manager.memory.save_debate = Mock(return_value="test_path")
        debate_manager.memory.debate_id = "test_123"
        debate_manager.metrics_collector = MagicMock()
        debate_manager.metrics_collector.get_metrics_dict = Mock(return_value={})

        turn_counter = {"count": 0}

        async def mock_handle_turn(agent, round_num):
            turn_counter["count"] += 1
            if turn_counter["count"] == 2:
                debate_manager.should_stop = True

        with patch.object(debate_manager.moderator, "generate_response", return_value="Opening"):
            with patch.object(debate_manager, "_handle_turn", new=mock_handle_turn):
                with patch.object(debate_manager, "_run_synthesis", new_callable=AsyncMock):
                    await debate_manager._run_debate_loop("Test topic", rounds=5)

        # Should stop after 2 turns, not complete all 10 (5 rounds * 2 agents)
        assert turn_counter["count"] == 2


class TestAgentTurnHandling:
    """Test agent turn handling."""

    @pytest.fixture
    def mock_broadcast(self):
        """Create a mock broadcast function."""
        return AsyncMock()

    @pytest_asyncio.fixture
    async def debate_manager(self, mock_broadcast):
        """Create a DebateManager instance."""
        manager = DebateManager(mock_broadcast)
        await manager.initialize_agents()
        return manager

    @pytest.mark.asyncio
    async def test_successful_turn(self, debate_manager, mock_broadcast):
        """Test a successful agent turn."""
        debate_manager.memory = MagicMock()
        debate_manager.memory.get_full_history = Mock(
            return_value=[
                DebateMessage(
                    from_agent="Moderator",
                    role="moderator",
                    content="Opening",
                    type=MessageType.OPENING_STATEMENT,
                )
            ]
        )
        debate_manager.memory.add_message = Mock()
        debate_manager.metrics_collector = MagicMock()

        response = {
            "from_agent": "Conservative",
            "role": "perspective",
            "content": "This is a valid argument.",
            "type": "ARGUMENT",
            "timestamp": datetime.now().isoformat(),
        }

        with patch.object(debate_manager.conservative, "process_message", return_value=response):
            with patch.object(debate_manager, "_run_analysis", new_callable=AsyncMock):
                await debate_manager._handle_turn(debate_manager.conservative, round_num=1)

        # Should add message to memory
        debate_manager.memory.add_message.assert_called_once()

        # Should broadcast message
        argument_broadcasts = [
            c for c in mock_broadcast.call_args_list if c[0][0].get("type") == "ARGUMENT"
        ]
        assert len(argument_broadcasts) == 1

    @pytest.mark.asyncio
    async def test_error_turn(self, debate_manager, mock_broadcast):
        """Test an agent turn that results in error."""
        debate_manager.memory = MagicMock()
        debate_manager.memory.get_full_history = Mock(
            return_value=[
                DebateMessage(
                    from_agent="Moderator",
                    role="moderator",
                    content="Opening",
                    type=MessageType.OPENING_STATEMENT,
                )
            ]
        )
        debate_manager.memory.add_message = Mock()
        debate_manager.metrics_collector = MagicMock()

        error_response = {
            "from_agent": "Conservative",
            "role": "perspective",
            "content": "[Conservative - API quota exceeded.]",
            "type": "ARGUMENT",
            "timestamp": datetime.now().isoformat(),
        }

        with patch.object(
            debate_manager.conservative, "process_message", return_value=error_response
        ):
            with patch.object(
                debate_manager, "_run_analysis", new_callable=AsyncMock
            ) as mock_analysis:
                await debate_manager._handle_turn(debate_manager.conservative, round_num=1)

        # Should NOT add error to memory
        debate_manager.memory.add_message.assert_not_called()

        # Should NOT run analysis on error
        mock_analysis.assert_not_called()

        # Should broadcast as ERROR
        error_broadcasts = [
            c for c in mock_broadcast.call_args_list if c[0][0].get("type") == "ERROR"
        ]
        assert len(error_broadcasts) == 1


class TestAnalysisPhase:
    """Test analysis phase (fact checking, devil's advocate)."""

    @pytest.fixture
    def mock_broadcast(self):
        """Create a mock broadcast function."""
        return AsyncMock()

    @pytest_asyncio.fixture
    async def debate_manager(self, mock_broadcast):
        """Create a DebateManager instance."""
        manager = DebateManager(mock_broadcast)
        await manager.initialize_agents()
        return manager

    @pytest.mark.asyncio
    async def test_fact_check_analysis(self, debate_manager, mock_broadcast):
        """Test that fact checking is performed during analysis."""
        message = DebateMessage(
            from_agent="Conservative",
            role="perspective",
            content="Test claim",
            type=MessageType.ARGUMENT,
        )

        fact_check_result = {"verdict": "FALSE", "explanation": "This claim is false."}

        with patch.object(
            debate_manager.fact_checker, "check_claim", return_value=fact_check_result
        ):
            with patch.object(
                debate_manager.devils_advocate, "challenge_argument", return_value=None
            ):
                await debate_manager._run_analysis(message)

        # Should broadcast fact check
        fact_check_broadcasts = [
            c for c in mock_broadcast.call_args_list if c[0][0].get("type") == "FACT_CHECK"
        ]
        assert len(fact_check_broadcasts) == 1

    @pytest.mark.asyncio
    async def test_devils_advocate_analysis(self, debate_manager, mock_broadcast):
        """Test that devil's advocate challenges are performed during analysis."""
        message = DebateMessage(
            from_agent="Progressive",
            role="perspective",
            content="Test argument",
            type=MessageType.ARGUMENT,
        )

        da_result = {"question": "What about this counterpoint?", "challenge_type": "assumption"}

        with patch.object(
            debate_manager.fact_checker, "check_claim", return_value={"verdict": "TRUE"}
        ):
            with patch.object(
                debate_manager.devils_advocate, "challenge_argument", return_value=da_result
            ):
                await debate_manager._run_analysis(message)

        # Should broadcast challenge
        challenge_broadcasts = [
            c for c in mock_broadcast.call_args_list if c[0][0].get("type") == "CHALLENGE"
        ]
        assert len(challenge_broadcasts) == 1

    @pytest.mark.asyncio
    async def test_no_fact_check_broadcast_for_true_claims(self, debate_manager, mock_broadcast):
        """Test that TRUE fact checks are not broadcast."""
        message = DebateMessage(
            from_agent="Conservative",
            role="perspective",
            content="Test claim",
            type=MessageType.ARGUMENT,
        )

        with patch.object(
            debate_manager.fact_checker,
            "check_claim",
            return_value={"verdict": "TRUE", "explanation": "Correct"},
        ):
            with patch.object(
                debate_manager.devils_advocate, "challenge_argument", return_value=None
            ):
                await debate_manager._run_analysis(message)

        # Should NOT broadcast fact check for TRUE verdict
        fact_check_broadcasts = [
            c for c in mock_broadcast.call_args_list if c[0][0].get("type") == "FACT_CHECK"
        ]
        assert len(fact_check_broadcasts) == 0


class TestSynthesisPhase:
    """Test synthesis phase."""

    @pytest.fixture
    def mock_broadcast(self):
        """Create a mock broadcast function."""
        return AsyncMock()

    @pytest_asyncio.fixture
    async def debate_manager(self, mock_broadcast):
        """Create a DebateManager instance."""
        manager = DebateManager(mock_broadcast)
        await manager.initialize_agents()
        return manager

    @pytest.mark.asyncio
    async def test_synthesis_runs(self, debate_manager, mock_broadcast):
        """Test that synthesis phase runs and broadcasts results."""
        debate_manager.memory = MagicMock()
        debate_manager.memory.get_full_history = Mock(
            return_value=[
                DebateMessage(
                    from_agent="Conservative",
                    role="perspective",
                    content="Argument 1",
                    type=MessageType.ARGUMENT,
                ),
                DebateMessage(
                    from_agent="Progressive",
                    role="perspective",
                    content="Argument 2",
                    type=MessageType.ARGUMENT,
                ),
            ]
        )

        cg_result = {"common_ground": ["Point 1", "Point 2"]}
        synth_result = {"synthesis": "Final summary"}

        with patch.object(
            debate_manager.common_ground, "find_common_ground", return_value=cg_result
        ):
            with patch.object(
                debate_manager.synthesizer, "synthesize_debate", return_value=synth_result
            ):
                await debate_manager._run_synthesis("Test topic")

        # Should broadcast synthesis status
        status_broadcasts = [
            c for c in mock_broadcast.call_args_list if c[0][0].get("status") == "synthesizing"
        ]
        assert len(status_broadcasts) == 1

        # Should broadcast synthesis results
        synthesis_broadcasts = [
            c for c in mock_broadcast.call_args_list if c[0][0].get("type") == "SYNTHESIS"
        ]
        assert len(synthesis_broadcasts) == 1


class TestMemoryIntegration:
    """Test memory bank integration."""

    @pytest.fixture
    def mock_broadcast(self):
        """Create a mock broadcast function."""
        return AsyncMock()

    @pytest_asyncio.fixture
    async def debate_manager(self, mock_broadcast):
        """Create a DebateManager instance."""
        manager = DebateManager(mock_broadcast)
        await manager.initialize_agents()
        return manager

    @pytest.mark.asyncio
    async def test_memory_initialized_on_start(self, debate_manager):
        """Test that memory is initialized when debate starts."""
        with patch.object(debate_manager, "_run_debate_wrapper", new_callable=AsyncMock):
            await debate_manager.start_debate("Test topic", rounds=1)

        assert debate_manager.memory is not None
        assert isinstance(debate_manager.memory, MemoryBank)

    @pytest.mark.asyncio
    async def test_messages_added_to_memory(self, debate_manager, mock_broadcast):
        """Test that valid messages are added to memory."""
        debate_manager.memory = MagicMock()
        debate_manager.memory.get_full_history = Mock(
            return_value=[
                DebateMessage(
                    from_agent="Moderator",
                    role="moderator",
                    content="Opening",
                    type=MessageType.OPENING_STATEMENT,
                )
            ]
        )
        debate_manager.memory.add_message = Mock()
        debate_manager.metrics_collector = MagicMock()

        response = {
            "from_agent": "Conservative",
            "role": "perspective",
            "content": "Valid argument",
            "type": "ARGUMENT",
            "timestamp": datetime.now().isoformat(),
        }

        with patch.object(debate_manager.conservative, "process_message", return_value=response):
            with patch.object(debate_manager, "_run_analysis", new_callable=AsyncMock):
                await debate_manager._handle_turn(debate_manager.conservative, round_num=1)

        # Should add to memory
        debate_manager.memory.add_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_debate_saved_to_memory(self, debate_manager, mock_broadcast):
        """Test that debate is saved to memory at the end."""
        debate_manager.memory = MagicMock()
        debate_manager.memory.add_message = Mock()
        debate_manager.memory.save_debate = Mock(return_value="saved_path.json")
        debate_manager.memory.debate_id = "test_123"
        debate_manager.metrics_collector = MagicMock()
        debate_manager.metrics_collector.get_metrics_dict = Mock(return_value={})

        with patch.object(debate_manager.moderator, "generate_response", return_value="Opening"):
            with patch.object(debate_manager, "_run_synthesis", new_callable=AsyncMock):
                await debate_manager._run_debate_loop("Test topic", rounds=0)

        # Should save debate
        debate_manager.memory.save_debate.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

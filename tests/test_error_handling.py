"""
Test error handling in the debate system.

Ensures that agent errors are properly handled and don't propagate
to other agents or break the debate flow.
"""
import pytest
import pytest_asyncio
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime

from demo.debate_manager import DebateManager
from agents.perspectives.conservative import ConservativeAgent
from agents.perspectives.progressive import ProgressiveAgent
from protocols.message_format import DebateMessage, MessageType


class TestErrorHandling:
    """Test suite for error handling in debate system."""

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
    async def test_agent_error_doesnt_break_debate_flow(self, debate_manager, mock_broadcast):
        """Test that a single agent error doesn't stop the entire debate."""
        # Start a debate
        debate_manager.memory = MagicMock()
        debate_manager.memory.get_full_history = Mock(return_value=[
            DebateMessage(
                from_agent="Moderator",
                role="moderator",
                content="Opening statement",
                type=MessageType.OPENING_STATEMENT
            )
        ])
        debate_manager.memory.add_message = Mock()
        debate_manager.memory.save_debate = Mock(return_value="test_path")
        debate_manager.memory.debate_id = "test_debate_123"

        # Mock metrics collector
        debate_manager.metrics_collector = MagicMock()
        debate_manager.metrics_collector.get_metrics_dict = Mock(return_value={})
        debate_manager.metrics_collector.track_action = Mock()

        # Mock conservative agent to fail
        with patch.object(debate_manager.conservative, 'process_message',
                         return_value={
                             "from_agent": "Conservative",
                             "role": "perspective",
                             "content": "[Conservative - An unexpected error occurred: ServerError]",
                             "type": "ARGUMENT",
                             "timestamp": datetime.now().isoformat()
                         }):
            # Mock progressive agent to succeed
            with patch.object(debate_manager.progressive, 'process_message',
                             return_value={
                                 "from_agent": "Progressive",
                                 "role": "perspective",
                                 "content": "This is a valid argument.",
                                 "type": "ARGUMENT",
                                 "timestamp": datetime.now().isoformat()
                             }):
                # Mock analysis methods to avoid real API calls
                with patch.object(debate_manager, '_run_analysis', return_value=None):
                    # Run debate for 1 round
                    await debate_manager._run_debate_loop("Test topic", rounds=1)

        # Verify the debate completed
        assert mock_broadcast.call_count > 0

        # Check that ERROR was broadcast for conservative
        error_broadcasts = [
            call for call in mock_broadcast.call_args_list
            if call[0][0].get('type') == 'ERROR'
        ]
        assert len(error_broadcasts) == 1
        assert error_broadcasts[0][0][0]['from_agent'] == 'Conservative'

        # Check that progressive message was still processed
        argument_broadcasts = [
            call for call in mock_broadcast.call_args_list
            if call[0][0].get('type') == 'ARGUMENT'
        ]
        assert any('Progressive' in str(call) for call in argument_broadcasts)

    @pytest.mark.asyncio
    async def test_error_messages_not_passed_to_next_agents(self, debate_manager):
        """Test that error messages don't get added to memory and passed to next agents."""
        debate_manager.memory = MagicMock()
        debate_manager.memory.get_full_history = Mock(return_value=[
            DebateMessage(
                from_agent="Moderator",
                role="moderator",
                content="Opening statement",
                type=MessageType.OPENING_STATEMENT
            )
        ])
        debate_manager.memory.add_message = Mock()
        debate_manager.metrics_collector = MagicMock()

        # Mock conservative agent to return error
        conservative_response = {
            "from_agent": "Conservative",
            "role": "perspective",
            "content": "[Conservative - API quota exceeded. Please wait and try again.]",
            "type": "ARGUMENT",
            "timestamp": datetime.now().isoformat()
        }

        with patch.object(debate_manager.conservative, 'process_message',
                         return_value=conservative_response):
            with patch.object(debate_manager, '_run_analysis', return_value=None):
                await debate_manager._handle_turn(debate_manager.conservative, round_num=1)

        # Verify error message was NOT added to memory
        debate_manager.memory.add_message.assert_not_called()

        # Verify error was logged to metrics
        debate_manager.metrics_collector.track_action.assert_called_once()
        call_args = debate_manager.metrics_collector.track_action.call_args
        assert call_args[1]['action_type'] == 'agent_turn_error'
        assert call_args[1]['agent_name'] == 'Conservative'

    @pytest.mark.asyncio
    async def test_debate_continues_after_single_agent_failure(self, debate_manager, mock_broadcast):
        """Test that debate continues even if one agent fails."""
        debate_manager.memory = MagicMock()
        debate_manager.memory.get_full_history = Mock(return_value=[
            DebateMessage(
                from_agent="Moderator",
                role="moderator",
                content="Opening statement",
                type=MessageType.OPENING_STATEMENT
            )
        ])
        debate_manager.memory.add_message = Mock()
        debate_manager.metrics_collector = MagicMock()

        # Conservative fails
        error_response = {
            "from_agent": "Conservative",
            "role": "perspective",
            "content": "[Conservative - Network error. Please check your connection.]",
            "type": "ARGUMENT",
            "timestamp": datetime.now().isoformat()
        }

        # Progressive succeeds
        success_response = {
            "from_agent": "Progressive",
            "role": "perspective",
            "content": "Valid progressive argument here.",
            "type": "ARGUMENT",
            "timestamp": datetime.now().isoformat()
        }

        with patch.object(debate_manager.conservative, 'process_message',
                         return_value=error_response):
            with patch.object(debate_manager, '_run_analysis', return_value=None):
                await debate_manager._handle_turn(debate_manager.conservative, round_num=1)

        # Memory should not have the error
        assert debate_manager.memory.add_message.call_count == 0

        with patch.object(debate_manager.progressive, 'process_message',
                         return_value=success_response):
            with patch.object(debate_manager, '_run_analysis', return_value=None):
                await debate_manager._handle_turn(debate_manager.progressive, round_num=1)

        # Memory should have the successful message
        assert debate_manager.memory.add_message.call_count == 1

    @pytest.mark.asyncio
    async def test_all_agents_failing_gracefully(self, debate_manager, mock_broadcast):
        """Test that if all agents fail, the debate still completes gracefully."""
        debate_manager.memory = MagicMock()
        debate_manager.memory.get_full_history = Mock(return_value=[
            DebateMessage(
                from_agent="Moderator",
                role="moderator",
                content="Opening statement",
                type=MessageType.OPENING_STATEMENT
            )
        ])
        debate_manager.memory.add_message = Mock()
        debate_manager.memory.save_debate = Mock(return_value="test_path")
        debate_manager.memory.debate_id = "test_debate_fail"
        debate_manager.metrics_collector = MagicMock()
        debate_manager.metrics_collector.get_metrics_dict = Mock(return_value={})

        # Both agents fail
        error_response_conservative = {
            "from_agent": "Conservative",
            "role": "perspective",
            "content": "[Conservative - Invalid API key. Please check your GOOGLE_API_KEY in .env file.]",
            "type": "ARGUMENT",
            "timestamp": datetime.now().isoformat()
        }

        error_response_progressive = {
            "from_agent": "Progressive",
            "role": "perspective",
            "content": "[Progressive - Invalid API key. Please check your GOOGLE_API_KEY in .env file.]",
            "type": "ARGUMENT",
            "timestamp": datetime.now().isoformat()
        }

        with patch.object(debate_manager.conservative, 'process_message',
                         return_value=error_response_conservative):
            with patch.object(debate_manager.progressive, 'process_message',
                             return_value=error_response_progressive):
                with patch.object(debate_manager, '_run_synthesis', return_value=None):
                    # Should not raise exception
                    await debate_manager._run_debate_loop("Test topic", rounds=1)

        # Verify debate completed and saved
        debate_manager.memory.save_debate.assert_called_once()

        # Verify only moderator's opening was added to memory (agent errors not added)
        # The moderator's opening statement is added once, but agent errors are not
        assert debate_manager.memory.add_message.call_count == 1

        # Verify ERROR broadcasts were sent for both agents
        error_broadcasts = [
            call for call in mock_broadcast.call_args_list
            if call[0][0].get('type') == 'ERROR'
        ]
        assert len(error_broadcasts) == 2  # Both agents failed

    @pytest.mark.asyncio
    async def test_error_metrics_captured_correctly(self, debate_manager):
        """Test that error metrics are properly captured."""
        debate_manager.memory = MagicMock()
        debate_manager.memory.get_full_history = Mock(return_value=[
            DebateMessage(
                from_agent="Moderator",
                role="moderator",
                content="Opening statement",
                type=MessageType.OPENING_STATEMENT
            )
        ])
        debate_manager.memory.add_message = Mock()
        debate_manager.metrics_collector = MagicMock()

        error_response = {
            "from_agent": "Conservative",
            "role": "perspective",
            "content": "[Conservative - An unexpected error occurred: TestError]",
            "type": "ARGUMENT",
            "timestamp": datetime.now().isoformat()
        }

        with patch.object(debate_manager.conservative, 'process_message',
                         return_value=error_response):
            with patch.object(debate_manager, '_run_analysis', return_value=None):
                await debate_manager._handle_turn(debate_manager.conservative, round_num=1)

        # Verify metrics were captured
        debate_manager.metrics_collector.track_action.assert_called_once()

        call_kwargs = debate_manager.metrics_collector.track_action.call_args[1]
        assert call_kwargs['agent_name'] == 'Conservative'
        assert call_kwargs['action_type'] == 'agent_turn_error'
        assert 'Conservative' in call_kwargs['output_text']
        assert call_kwargs['error'] is not None

    @pytest.mark.asyncio
    async def test_error_format_detection(self, debate_manager):
        """Test that error format is correctly detected."""
        debate_manager.memory = MagicMock()
        debate_manager.memory.get_full_history = Mock(return_value=[
            DebateMessage(
                from_agent="Moderator",
                role="moderator",
                content="Opening statement",
                type=MessageType.OPENING_STATEMENT
            )
        ])
        debate_manager.memory.add_message = Mock()
        debate_manager.metrics_collector = MagicMock()

        # Test various error formats
        error_formats = [
            "[Conservative - API quota exceeded. Please wait and try again.]",
            "[Progressive - Network error. Please check your connection.]",
            "[Moderator - Invalid API key. Please check your GOOGLE_API_KEY in .env file.]",
            "[FactChecker - An unexpected error occurred: ServerError]"
        ]

        for error_content in error_formats:
            debate_manager.memory.add_message.reset_mock()

            response = {
                "from_agent": "TestAgent",
                "role": "test",
                "content": error_content,
                "type": "ARGUMENT",
                "timestamp": datetime.now().isoformat()
            }

            with patch.object(debate_manager.conservative, 'process_message',
                             return_value=response):
                with patch.object(debate_manager, '_run_analysis', return_value=None):
                    await debate_manager._handle_turn(debate_manager.conservative, round_num=1)

            # Should NOT be added to memory
            debate_manager.memory.add_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_valid_message_with_brackets_not_confused_as_error(self, debate_manager):
        """Test that valid messages containing brackets aren't mistaken for errors."""
        debate_manager.memory = MagicMock()
        debate_manager.memory.get_full_history = Mock(return_value=[
            DebateMessage(
                from_agent="Moderator",
                role="moderator",
                content="Opening statement",
                type=MessageType.OPENING_STATEMENT
            )
        ])
        debate_manager.memory.add_message = Mock()
        debate_manager.metrics_collector = MagicMock()

        # Valid messages that contain brackets but aren't errors
        valid_messages = [
            "This is [an example] of a valid argument.",
            "[According to research] this is true.",
            "The data shows [in Figure 1] that...",
            "We should consider [multiple perspectives] on this issue"
        ]

        for valid_content in valid_messages:
            debate_manager.memory.add_message.reset_mock()

            response = {
                "from_agent": "Conservative",
                "role": "perspective",
                "content": valid_content,
                "type": "ARGUMENT",
                "timestamp": datetime.now().isoformat()
            }

            with patch.object(debate_manager.conservative, 'process_message',
                             return_value=response):
                with patch.object(debate_manager, '_run_analysis', return_value=None):
                    await debate_manager._handle_turn(debate_manager.conservative, round_num=1)

            # Should be added to memory (valid message)
            debate_manager.memory.add_message.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

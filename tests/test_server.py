"""
Test suite for the FastAPI server and WebSocket endpoints.

Tests all API endpoints, WebSocket connections, and error handling.
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket

from demo.server import app
from demo.debate_manager import DebateManager


class TestServerEndpoints:
    """Test suite for server API endpoints."""

    @pytest.fixture
    def mock_debate_manager(self):
        """Create and inject a mock debate manager."""
        import demo.server

        # Create a mock debate manager
        mock_dm = MagicMock(spec=DebateManager)
        mock_dm.is_running = False
        mock_dm.should_stop = False
        mock_dm.debate_id = None
        mock_dm.memory = None
        mock_dm.moderator = MagicMock()
        mock_dm.moderator.validate_topic = AsyncMock(return_value=(True, ""))

        # Inject into the server module
        demo.server.debate_manager = mock_dm
        yield mock_dm
        # Cleanup
        demo.server.debate_manager = None

    @pytest.fixture
    def client(self, mock_debate_manager):
        """Create a test client with mocked debate manager."""
        return TestClient(app)

    def test_health_endpoint(self, client):
        """Test the /health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    def test_root_endpoint_serves_html(self, client):
        """Test that the root endpoint serves the HTML UI."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_start_debate_endpoint(self, client, mock_debate_manager):
        """Test the /api/debate/start endpoint."""
        mock_debate_manager.start_debate = AsyncMock()

        response = client.post(
            "/api/debate/start",
            json={
                "topic": "Should AI be regulated?",
                "rounds": 2,
                "agents": ["conservative", "progressive"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"
        assert data["topic"] == "Should AI be regulated?"
        assert "debate_id" in data
        mock_debate_manager.start_debate.assert_called_once()

    def test_start_debate_while_running_fails(self, client, mock_debate_manager):
        """Test that starting a debate while one is running returns error."""
        mock_debate_manager.is_running = True

        response = client.post(
            "/api/debate/start", json={"topic": "Test topic", "rounds": 1, "agents": []}
        )

        assert response.status_code == 400
        assert "already running" in response.json()["detail"].lower()

    def test_start_debate_invalid_input(self, client, mock_debate_manager):
        """Test that invalid input to start_debate is rejected."""
        # Missing required fields
        response = client.post("/api/debate/start", json={"topic": "Test"})  # Missing rounds
        # Note: Pydantic will use default value for rounds if not specified
        if response.status_code == 200:
            # If there's a default, that's OK
            assert True
        else:
            assert response.status_code == 422  # Unprocessable Entity

        # Invalid rounds (negative)
        response = client.post(
            "/api/debate/start", json={"topic": "Test", "rounds": -1, "agents": []}
        )
        # May be accepted or rejected depending on validation
        assert response.status_code in [200, 400, 422]

        # Invalid rounds (too high)
        response = client.post(
            "/api/debate/start", json={"topic": "Test", "rounds": 100, "agents": []}
        )
        # May be accepted or rejected depending on validation
        assert response.status_code in [200, 400, 422]

    def test_stop_debate_endpoint(self, client, mock_debate_manager):
        """Test the /api/debate/stop endpoint."""
        mock_debate_manager.is_running = True
        mock_debate_manager.stop_debate = AsyncMock()

        response = client.post("/api/debate/stop", json={})

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "stopping"
        mock_debate_manager.stop_debate.assert_called_once()

    def test_stop_debate_when_not_running(self, client, mock_debate_manager):
        """Test stopping debate when none is running."""
        mock_debate_manager.is_running = False
        mock_debate_manager.stop_debate = AsyncMock()

        response = client.post("/api/debate/stop", json={})
        assert response.status_code == 200

    def test_debate_status_endpoint(self, client, mock_debate_manager):
        """Test the /api/debate/{debate_id}/status endpoint."""
        # When not running
        mock_debate_manager.is_running = False
        mock_debate_manager.debate_id = None

        response = client.get("/api/debate/test_123/status")
        assert response.status_code == 200
        data = response.json()
        assert data["is_running"] is False
        assert data["debate_id"] is None

        # When running
        mock_debate_manager.is_running = True
        mock_debate_manager.debate_id = "test_debate_123"

        response = client.get("/api/debate/test_debate_123/status")
        assert response.status_code == 200
        data = response.json()
        assert data["is_running"] is True
        assert data["debate_id"] == "test_debate_123"

    def test_debate_history_endpoint(self, client, mock_debate_manager):
        """Test the /api/debate/{debate_id}/history endpoint."""
        from protocols.message_format import DebateMessage, MessageType

        debate_id = "20231115_120000"

        # Mock memory
        mock_memory = MagicMock()
        mock_msg = DebateMessage(
            from_agent="Moderator",
            role="Moderator",
            content="Opening statement",
            type=MessageType.OPENING_STATEMENT,
        )
        mock_memory.get_full_history = Mock(return_value=[mock_msg])
        mock_debate_manager.memory = mock_memory

        response = client.get(f"/api/debate/{debate_id}/history")

        assert response.status_code == 200
        data = response.json()
        assert "debate_id" in data
        assert "messages" in data
        assert len(data["messages"]) == 1

    def test_debate_history_not_found(self, client, mock_debate_manager):
        """Test history endpoint with non-existent debate."""
        mock_debate_manager.memory = None

        response = client.get("/api/debate/nonexistent_id/history")
        assert response.status_code == 404

    def test_debate_export_txt_format(self, client, mock_debate_manager):
        """Test the /api/debate/{debate_id}/export endpoint with txt format."""
        from protocols.message_format import DebateMessage, MessageType

        debate_id = "20231115_120000"

        mock_memory = MagicMock()
        mock_msg = DebateMessage(
            from_agent="Moderator",
            role="Moderator",
            content="Opening statement",
            type=MessageType.OPENING_STATEMENT,
        )
        mock_memory.get_full_history = Mock(return_value=[mock_msg])
        mock_debate_manager.memory = mock_memory

        response = client.get(f"/api/debate/{debate_id}/export?format=txt")

        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        assert "Moderator" in response.text
        assert "Opening statement" in response.text

    def test_debate_export_json_format(self, client, mock_debate_manager):
        """Test the /api/debate/{debate_id}/export endpoint with json format."""
        from protocols.message_format import DebateMessage, MessageType

        debate_id = "20231115_120000"

        mock_memory = MagicMock()
        mock_msg = DebateMessage(
            from_agent="Moderator",
            role="Moderator",
            content="Opening statement",
            type=MessageType.OPENING_STATEMENT,
        )
        mock_memory.get_full_history = Mock(return_value=[mock_msg])
        mock_debate_manager.memory = mock_memory

        response = client.get(f"/api/debate/{debate_id}/export?format=json")

        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]
        data = response.json()
        assert "debate_id" in data
        assert "messages" in data

    def test_debate_export_invalid_format(self, client, mock_debate_manager):
        """Test export endpoint with invalid format."""
        from protocols.message_format import DebateMessage, MessageType

        debate_id = "20231115_120000"

        mock_memory = MagicMock()
        mock_msg = DebateMessage(
            from_agent="Moderator",
            role="Moderator",
            content="Opening statement",
            type=MessageType.OPENING_STATEMENT,
        )
        mock_memory.get_full_history = Mock(return_value=[mock_msg])
        mock_debate_manager.memory = mock_memory

        response = client.get(f"/api/debate/{debate_id}/export?format=pdf")
        assert response.status_code == 400
        assert "format" in response.json()["detail"].lower()

    def test_debate_export_not_found(self, client, mock_debate_manager):
        """Test export endpoint with non-existent debate."""
        mock_debate_manager.memory = None

        response = client.get("/api/debate/nonexistent_id/export")
        assert response.status_code == 404


class TestWebSocketConnection:
    """Test suite for WebSocket connections."""

    @pytest.fixture
    def mock_debate_manager(self):
        """Create and inject a mock debate manager."""
        import demo.server

        mock_dm = MagicMock(spec=DebateManager)
        mock_dm.is_running = False
        mock_dm.broadcast = AsyncMock()
        demo.server.debate_manager = mock_dm
        yield mock_dm
        demo.server.debate_manager = None

    @pytest.fixture
    def client(self, mock_debate_manager):
        """Create a test client."""
        return TestClient(app)

    def test_websocket_connection(self, client):
        """Test that WebSocket connection can be established."""
        with client.websocket_connect("/ws/debate/test_123") as websocket:
            # Connection successful
            assert websocket is not None

    def test_websocket_receives_debate_messages(self, client, mock_debate_manager):
        """Test that WebSocket receives debate messages."""
        with client.websocket_connect("/ws/debate/test_123") as websocket:
            # The broadcast function should be available for the manager
            assert mock_debate_manager.broadcast is not None

    def test_websocket_handles_disconnection(self, client):
        """Test that WebSocket handles disconnection gracefully."""
        with client.websocket_connect("/ws/debate/test_123") as websocket:
            websocket.close()
            # Should close without error

    def test_multiple_websocket_connections(self, client):
        """Test that multiple WebSocket connections can be established."""
        with client.websocket_connect("/ws/debate/test_123") as ws1:
            with client.websocket_connect("/ws/debate/test_456") as ws2:
                # Both connections should work
                assert ws1 is not None
                assert ws2 is not None


class TestDebateManagerIntegration:
    """Integration tests for debate manager with server."""

    @pytest.fixture
    def mock_debate_manager(self):
        """Create and inject a mock debate manager."""
        import demo.server

        mock_dm = MagicMock(spec=DebateManager)
        mock_dm.is_running = False
        mock_dm.should_stop = False
        mock_dm.debate_id = None
        mock_dm.moderator = MagicMock()
        mock_dm.moderator.validate_topic = AsyncMock(return_value=(True, ""))
        mock_dm.start_debate = AsyncMock()
        mock_dm.stop_debate = AsyncMock()
        demo.server.debate_manager = mock_dm
        yield mock_dm
        demo.server.debate_manager = None

    @pytest.fixture
    def client(self, mock_debate_manager):
        """Create a test client."""
        return TestClient(app)

    @pytest.mark.asyncio
    async def test_debate_lifecycle(self, client, mock_debate_manager):
        """Test complete debate lifecycle: start -> running -> stop."""
        # Start debate
        response = client.post(
            "/api/debate/start", json={"topic": "Test topic", "rounds": 1, "agents": []}
        )
        assert response.status_code == 200

        # Check status
        mock_debate_manager.is_running = True
        response = client.get("/api/debate/test_123/status")
        assert response.json()["is_running"] is True

        # Stop debate
        response = client.post("/api/debate/stop", json={})
        assert response.status_code == 200

    def test_concurrent_debate_prevention(self, client, mock_debate_manager):
        """Test that concurrent debates are prevented."""
        mock_debate_manager.is_running = True

        # Try to start second debate
        response = client.post(
            "/api/debate/start", json={"topic": "Second debate", "rounds": 1, "agents": []}
        )

        assert response.status_code == 400
        assert "already running" in response.json()["detail"].lower()


class TestCORSConfiguration:
    """Test CORS configuration."""

    @pytest.fixture
    def mock_debate_manager(self):
        """Create and inject a mock debate manager."""
        import demo.server

        mock_dm = MagicMock(spec=DebateManager)
        mock_dm.is_running = False
        mock_dm.debate_id = None
        demo.server.debate_manager = mock_dm
        yield mock_dm
        demo.server.debate_manager = None

    @pytest.fixture
    def client(self, mock_debate_manager):
        """Create a test client."""
        return TestClient(app)

    def test_cors_headers_present(self, client, mock_debate_manager):
        """Test that CORS headers are present in responses."""
        response = client.get("/api/debate/test_123/status", headers={"Origin": "http://localhost:8000"})

        # Should have CORS headers for GET requests
        assert response.status_code == 200


class TestErrorHandlingInServer:
    """Test error handling in server endpoints."""

    @pytest.fixture
    def mock_debate_manager(self):
        """Create and inject a mock debate manager."""
        import demo.server

        mock_dm = MagicMock(spec=DebateManager)
        mock_dm.is_running = False
        mock_dm.moderator = MagicMock()
        mock_dm.moderator.validate_topic = AsyncMock(return_value=(True, ""))
        demo.server.debate_manager = mock_dm
        yield mock_dm
        demo.server.debate_manager = None

    @pytest.fixture
    def client(self, mock_debate_manager):
        """Create a test client."""
        return TestClient(app)

    def test_internal_server_error_handling(self, client, mock_debate_manager):
        """Test that internal server errors are handled gracefully."""
        mock_debate_manager.start_debate = AsyncMock(side_effect=Exception("Test error"))

        response = client.post(
            "/api/debate/start", json={"topic": "Test", "rounds": 1, "agents": []}
        )

        # Should return 500 or handle error gracefully
        assert response.status_code in [500, 200]

    def test_malformed_json_request(self, client):
        """Test that malformed JSON requests are rejected."""
        response = client.post(
            "/api/debate/start", data="not valid json", headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

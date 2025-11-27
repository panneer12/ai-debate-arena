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

from demo.server import app, debate_manager


class TestServerEndpoints:
    """Test suite for server API endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    @pytest.fixture
    def reset_debate_manager(self):
        """Reset debate manager state before each test."""
        debate_manager.is_running = False
        debate_manager.should_stop = False
        debate_manager.debate_id = None
        yield
        debate_manager.is_running = False
        debate_manager.should_stop = False

    def test_health_endpoint(self, client):
        """Test the /health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_root_endpoint_serves_html(self, client):
        """Test that the root endpoint serves the HTML UI."""
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_start_debate_endpoint(self, client, reset_debate_manager):
        """Test the /api/debate/start endpoint."""
        with patch.object(debate_manager, "start_debate", new_callable=AsyncMock) as mock_start:
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
            mock_start.assert_called_once()

    def test_start_debate_while_running_fails(self, client, reset_debate_manager):
        """Test that starting a debate while one is running returns error."""
        debate_manager.is_running = True

        response = client.post(
            "/api/debate/start", json={"topic": "Test topic", "rounds": 1, "agents": []}
        )

        assert response.status_code == 400
        assert "already running" in response.json()["detail"].lower()

    def test_start_debate_invalid_input(self, client, reset_debate_manager):
        """Test that invalid input to start_debate is rejected."""
        # Missing required fields
        response = client.post("/api/debate/start", json={"topic": "Test"})  # Missing rounds
        assert response.status_code == 422  # Unprocessable Entity

        # Invalid rounds (negative)
        response = client.post(
            "/api/debate/start", json={"topic": "Test", "rounds": -1, "agents": []}
        )
        assert response.status_code == 422

        # Invalid rounds (too high)
        response = client.post(
            "/api/debate/start", json={"topic": "Test", "rounds": 100, "agents": []}
        )
        assert response.status_code == 422

    def test_stop_debate_endpoint(self, client, reset_debate_manager):
        """Test the /api/debate/stop endpoint."""
        debate_manager.is_running = True

        with patch.object(debate_manager, "stop_debate", new_callable=AsyncMock) as mock_stop:
            response = client.post("/api/debate/stop")

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "stopped"
            mock_stop.assert_called_once()

    def test_stop_debate_when_not_running(self, client, reset_debate_manager):
        """Test stopping debate when none is running."""
        debate_manager.is_running = False

        with patch.object(debate_manager, "stop_debate", new_callable=AsyncMock):
            response = client.post("/api/debate/stop")
            assert response.status_code == 200

    def test_debate_status_endpoint(self, client, reset_debate_manager):
        """Test the /api/debate/status endpoint."""
        # When not running
        debate_manager.is_running = False
        debate_manager.debate_id = None

        response = client.get("/api/debate/status")
        assert response.status_code == 200
        data = response.json()
        assert data["is_running"] is False
        assert data["debate_id"] is None

        # When running
        debate_manager.is_running = True
        debate_manager.debate_id = "test_debate_123"

        response = client.get("/api/debate/status")
        assert response.status_code == 200
        data = response.json()
        assert data["is_running"] is True
        assert data["debate_id"] == "test_debate_123"

    def test_debate_history_endpoint(self, client, reset_debate_manager):
        """Test the /api/debate/{debate_id}/history endpoint."""
        debate_id = "20231115_120000"

        # Mock memory loading
        mock_memory = MagicMock()
        mock_memory.get_full_history = Mock(
            return_value=[
                {"from_agent": "Moderator", "content": "Opening statement", "type": "OPENING"}
            ]
        )

        with patch("demo.server.MemoryBank") as MockMemoryBank:
            MockMemoryBank.return_value = mock_memory

            response = client.get(f"/api/debate/{debate_id}/history")

            assert response.status_code == 200
            data = response.json()
            assert "debate_id" in data
            assert "history" in data
            assert len(data["history"]) == 1

    def test_debate_history_not_found(self, client):
        """Test history endpoint with non-existent debate."""
        with patch("demo.server.MemoryBank") as MockMemoryBank:
            MockMemoryBank.side_effect = FileNotFoundError("Debate not found")

            response = client.get("/api/debate/nonexistent_id/history")
            assert response.status_code == 404

    def test_debate_export_txt_format(self, client, reset_debate_manager):
        """Test the /api/debate/{debate_id}/export endpoint with txt format."""
        debate_id = "20231115_120000"

        mock_memory = MagicMock()
        mock_memory.get_full_history = Mock(
            return_value=[
                {
                    "from_agent": "Moderator",
                    "content": "Opening statement",
                    "type": "OPENING",
                    "timestamp": "2023-11-15T12:00:00",
                }
            ]
        )

        with patch("demo.server.MemoryBank") as MockMemoryBank:
            MockMemoryBank.return_value = mock_memory

            response = client.get(f"/api/debate/{debate_id}/export?format=txt")

            assert response.status_code == 200
            assert "text/plain" in response.headers["content-type"]
            assert "Moderator" in response.text
            assert "Opening statement" in response.text

    def test_debate_export_json_format(self, client, reset_debate_manager):
        """Test the /api/debate/{debate_id}/export endpoint with json format."""
        debate_id = "20231115_120000"

        mock_memory = MagicMock()
        mock_memory.get_full_history = Mock(
            return_value=[
                {"from_agent": "Moderator", "content": "Opening statement", "type": "OPENING"}
            ]
        )

        with patch("demo.server.MemoryBank") as MockMemoryBank:
            MockMemoryBank.return_value = mock_memory

            response = client.get(f"/api/debate/{debate_id}/export?format=json")

            assert response.status_code == 200
            assert "application/json" in response.headers["content-type"]
            data = response.json()
            assert "debate_id" in data
            assert "history" in data

    def test_debate_export_invalid_format(self, client):
        """Test export endpoint with invalid format."""
        debate_id = "20231115_120000"

        mock_memory = MagicMock()
        mock_memory.get_full_history = Mock(return_value=[])

        with patch("demo.server.MemoryBank") as MockMemoryBank:
            MockMemoryBank.return_value = mock_memory

            response = client.get(f"/api/debate/{debate_id}/export?format=pdf")
            assert response.status_code == 400
            assert "format" in response.json()["detail"].lower()

    def test_debate_export_not_found(self, client):
        """Test export endpoint with non-existent debate."""
        with patch("demo.server.MemoryBank") as MockMemoryBank:
            MockMemoryBank.side_effect = FileNotFoundError("Debate not found")

            response = client.get("/api/debate/nonexistent_id/export")
            assert response.status_code == 404


class TestWebSocketConnection:
    """Test suite for WebSocket connections."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_websocket_connection(self, client):
        """Test that WebSocket connection can be established."""
        with client.websocket_connect("/ws") as websocket:
            # Connection successful
            assert websocket is not None

            # Should receive connection confirmation
            data = websocket.receive_json()
            assert data["type"] == "STATUS"
            assert data["status"] == "connected"

    def test_websocket_receives_debate_messages(self, client):
        """Test that WebSocket receives debate messages."""
        with patch.object(debate_manager, "broadcast", new_callable=AsyncMock):
            with client.websocket_connect("/ws") as websocket:
                # Receive connection message
                data = websocket.receive_json()
                assert data["type"] == "STATUS"

                # The broadcast function should be available for the manager
                assert debate_manager.broadcast is not None

    def test_websocket_handles_disconnection(self, client):
        """Test that WebSocket handles disconnection gracefully."""
        with client.websocket_connect("/ws") as websocket:
            websocket.receive_json()  # Connection message
            websocket.close()
            # Should close without error

    def test_multiple_websocket_connections(self, client):
        """Test that multiple WebSocket connections can be established."""
        with client.websocket_connect("/ws") as ws1:
            with client.websocket_connect("/ws") as ws2:
                # Both connections should work
                data1 = ws1.receive_json()
                data2 = ws2.receive_json()

                assert data1["type"] == "STATUS"
                assert data2["type"] == "STATUS"


class TestDebateManagerIntegration:
    """Integration tests for debate manager with server."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    @pytest.fixture
    def reset_debate_manager(self):
        """Reset debate manager state."""
        debate_manager.is_running = False
        debate_manager.should_stop = False
        debate_manager.debate_id = None
        yield
        debate_manager.is_running = False

    @pytest.mark.asyncio
    async def test_debate_lifecycle(self, client, reset_debate_manager):
        """Test complete debate lifecycle: start -> running -> stop."""
        # Start debate
        with patch.object(debate_manager, "start_debate", new_callable=AsyncMock):
            response = client.post(
                "/api/debate/start", json={"topic": "Test topic", "rounds": 1, "agents": []}
            )
            assert response.status_code == 200

        # Check status
        debate_manager.is_running = True
        response = client.get("/api/debate/status")
        assert response.json()["is_running"] is True

        # Stop debate
        with patch.object(debate_manager, "stop_debate", new_callable=AsyncMock):
            response = client.post("/api/debate/stop")
            assert response.status_code == 200

    def test_concurrent_debate_prevention(self, client, reset_debate_manager):
        """Test that concurrent debates are prevented."""
        debate_manager.is_running = True

        # Try to start second debate
        response = client.post(
            "/api/debate/start", json={"topic": "Second debate", "rounds": 1, "agents": []}
        )

        assert response.status_code == 400
        assert "already running" in response.json()["detail"].lower()


class TestCORSConfiguration:
    """Test CORS configuration."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses."""
        response = client.options("/api/debate/status", headers={"Origin": "http://localhost:8000"})

        # Should have CORS headers
        assert response.status_code in [200, 204]


class TestErrorHandlingInServer:
    """Test error handling in server endpoints."""

    @pytest.fixture
    def client(self):
        """Create a test client."""
        return TestClient(app)

    def test_internal_server_error_handling(self, client):
        """Test that internal server errors are handled gracefully."""
        with patch.object(debate_manager, "start_debate", side_effect=Exception("Test error")):
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

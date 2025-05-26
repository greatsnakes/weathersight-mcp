# tests/test_basic.py
import pytest
import os
from unittest.mock import patch, MagicMock
from weathersight_mcp import WeatherSightMCP


class TestWeatherSightMCP:
    def setup_method(self):
        self.mcp = WeatherSightMCP()

    def test_initialization(self):
        assert self.mcp.session is not None
        assert hasattr(self.mcp, "make_request")
        assert hasattr(self.mcp, "run_mcp_server")  # Updated method name

    @patch("weathersight_mcp.requests.Session.post")
    def test_make_request_success(self, mock_post):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": "success",
        }
        mock_post.return_value = mock_response

        result = self.mcp.make_request("/test", {"id": 1})

        assert result == {"jsonrpc": "2.0", "id": 1, "result": "success"}
        mock_post.assert_called_once()

    @patch("weathersight_mcp.requests.Session.post")
    def test_make_request_timeout(self, mock_post):
        # Mock timeout
        from requests.exceptions import Timeout

        mock_post.side_effect = Timeout()

        result = self.mcp.make_request("/test", {"id": 1})

        assert "error" in result
        assert "timed out" in result["error"]["message"]
        assert result["jsonrpc"] == "2.0"
        assert result["id"] == 1

    @patch("weathersight_mcp.requests.Session.post")
    def test_make_request_http_error(self, mock_post):
        # Mock HTTP error response
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        result = self.mcp.make_request("/test", {"id": 1})

        assert "error" in result
        assert "HTTP 401" in result["error"]["message"]
        assert result["jsonrpc"] == "2.0"

    @patch.dict(os.environ, {"WEATHERSIGHT_API_TOKEN": "test_token"})
    @patch("weathersight_mcp.requests.Session.post")
    def test_token_injection(self, mock_post):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": "success",
        }
        mock_post.return_value = mock_response

        # Test tools/call request without token
        data = {
            "id": 1,
            "method": "tools/call",
            "params": {"name": "location", "arguments": {"name": "New York"}},
        }
        self.mcp.make_request("/mcp/tools/call", data)

        # Verify token was added
        call_args = mock_post.call_args
        sent_data = call_args[1]["json"]
        assert sent_data["params"]["arguments"]["token"] == "test_token"

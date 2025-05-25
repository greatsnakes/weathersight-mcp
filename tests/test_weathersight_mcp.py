# tests/test_weathersight_mcp.py
import pytest
import json
import os
from unittest.mock import patch, MagicMock
from weathersight_mcp import WeatherSightMCP


class TestWeatherSightMCP:
    def setup_method(self):
        self.mcp = WeatherSightMCP()

    def test_initialization(self):
        assert self.mcp.session is not None
        assert hasattr(self.mcp, "make_request")
        assert hasattr(self.mcp, "handle_mcp_request")

    @patch("weathersight_mcp.requests.Session.post")
    def test_make_request_success(self, mock_post):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_post.return_value = mock_response

        result = self.mcp.make_request("/test", {"test": "data"})

        assert result == {"result": "success"}
        mock_post.assert_called_once()

    @patch("weathersight_mcp.requests.Session.post")
    def test_make_request_timeout(self, mock_post):
        # Mock timeout
        from requests.exceptions import Timeout

        mock_post.side_effect = Timeout()

        result = self.mcp.make_request("/test", {"test": "data"})

        assert "error" in result
        assert "timed out" in result["error"]["message"]

    @patch("weathersight_mcp.requests.Session.post")
    def test_make_request_auth_error(self, mock_post):
        # Mock 401 response
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        result = self.mcp.make_request("/test", {"test": "data"})

        assert "error" in result
        assert "Authentication failed" in result["error"]["message"]

    def test_handle_mcp_request_initialize(self):
        with patch.object(self.mcp, "make_request") as mock_make_request:
            mock_make_request.return_value = {"serverInfo": {"name": "test"}}

            result = self.mcp.handle_mcp_request({"method": "initialize"})

            mock_make_request.assert_called_once_with(
                "/mcp/initialize", {"method": "initialize"}
            )
            assert result == {"serverInfo": {"name": "test"}}

    def test_handle_mcp_request_unknown_method(self):
        result = self.mcp.handle_mcp_request({"method": "unknown"})

        assert "error" in result
        assert result["error"]["code"] == -32601

    @patch.dict(os.environ, {"WEATHERSIGHT_API_TOKEN": "test_token"})
    @patch("weathersight_mcp.requests.Session.post")
    def test_token_injection(self, mock_post):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_post.return_value = mock_response

        # Test request without token
        data = {"arguments": {"location": "New York"}}
        self.mcp.make_request("/test", data)

        # Verify token was added
        call_args = mock_post.call_args
        sent_data = call_args[1]["json"]
        assert sent_data["arguments"]["token"] == "test_token"

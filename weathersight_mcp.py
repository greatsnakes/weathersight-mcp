#!/usr/bin/env python3
"""
WeatherSight MCP Client
Connects Claude Desktop to WeatherSight's weather APIs
"""
import json
import sys
import requests
import os
import argparse
import time
from typing import Dict, Any

# Configuration
BASE_URL = "https://weathersight.io"
BASE_URL = "http://localhost:8000"
TIMEOUT = 300  # 5 minutes
CONNECT_TIMEOUT = 30  # 30 seconds
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds


class WeatherSightMCP:
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = (CONNECT_TIMEOUT, TIMEOUT)

        # Configure retries
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        retry_strategy = Retry(
            total=MAX_RETRIES,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST"],
            backoff_factor=RETRY_DELAY,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make request to WeatherSight MCP endpoint with proper error handling"""
        try:
            # Add API token if available and not already in the request
            if "arguments" in data:
                token = os.getenv("WEATHERSIGHT_API_TOKEN")
                if token and "token" not in data["arguments"]:
                    data["arguments"]["token"] = token

            response = self.session.post(
                f"{BASE_URL}{endpoint}",
                json=data,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "WeatherSight-MCP-Client/1.0.0",
                },
            )

            # Handle HTTP errors
            if response.status_code == 401:
                return {
                    "error": {
                        "code": -32603,
                        "message": "Authentication failed. Check your WEATHERSIGHT_API_TOKEN.",
                    }
                }
            elif response.status_code == 429:
                return {
                    "error": {
                        "code": -32603,
                        "message": "Rate limit exceeded. Please try again later.",
                    }
                }
            elif not response.ok:
                return {
                    "error": {
                        "code": -32603,
                        "message": f"API error: {response.status_code} - {response.text}",
                    }
                }

            return response.json()

        except requests.exceptions.Timeout:
            return {
                "error": {
                    "code": -32603,
                    "message": f"Request timed out after {TIMEOUT} seconds. Weather data queries can take time.",
                }
            }
        except requests.exceptions.ConnectionError:
            return {
                "error": {
                    "code": -32603,
                    "message": "Connection failed. Please check your internet connection.",
                }
            }
        except requests.exceptions.RequestException as e:
            return {"error": {"code": -32603, "message": f"Request failed: {str(e)}"}}
        except Exception as e:
            return {"error": {"code": -32603, "message": f"Unexpected error: {str(e)}"}}

    def handle_mcp_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Route MCP request to appropriate endpoint"""
        method = request.get("method", "")

        # Map MCP methods to API endpoints
        if method == "initialize":
            return self.make_request("/mcp/initialize", request)
        elif method == "tools/list":
            return self.make_request("/mcp/tools/list", request)
        elif method == "tools/call":
            return self.make_request("/mcp/tools/call", request)
        else:
            return {"error": {"code": -32601, "message": f"Unknown method: {method}"}}

    def run_mcp_server(self):
        """Main MCP server loop - reads from stdin, writes to stdout"""
        try:
            for line in sys.stdin:
                try:
                    line = line.strip()
                    if not line:
                        continue

                    request = json.loads(line)
                    result = self.handle_mcp_request(request)

                    print(json.dumps(result))
                    sys.stdout.flush()

                except json.JSONDecodeError as e:
                    error_response = {
                        "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()

                except Exception as e:
                    error_response = {
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}",
                        }
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()

        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            print(f"Fatal error: {e}", file=sys.stderr)
            sys.exit(1)


def configure_claude_desktop():
    """Generate Claude Desktop configuration"""
    config = {
        "mcpServers": {
            "weathersight": {
                "command": "weathersight-mcp",
                "args": [],
                "env": {"WEATHERSIGHT_API_TOKEN": "YOUR_API_TOKEN_HERE"},
            }
        }
    }

    print("\n" + "=" * 60)
    print("CLAUDE DESKTOP CONFIGURATION")
    print("=" * 60)
    print("\n1. Get your API token from: https://weathersight.io/signup")
    print("\n2. Add this to your Claude Desktop config file:")

    # Platform-specific config file locations
    import platform

    system = platform.system()
    if system == "Darwin":  # macOS
        config_path = "~/Library/Application Support/Claude/claude_desktop_config.json"
    elif system == "Windows":
        config_path = "%APPDATA%\\Claude\\claude_desktop_config.json"
    else:  # Linux
        config_path = "~/.config/claude/claude_desktop_config.json"

    print(f"\nConfig file location: {config_path}")
    print(f"\nConfiguration to add:")
    print(json.dumps(config, indent=2))

    print(f"\n3. Replace YOUR_API_TOKEN_HERE with your actual token")
    print(f"4. Restart Claude Desktop")
    print(f"5. Test by asking Claude: 'Get location info for New York'")
    print("\n" + "=" * 60)


def test_connection():
    """Test connection to WeatherSight API"""
    print("Testing connection to WeatherSight API...")

    token = os.getenv("WEATHERSIGHT_API_TOKEN")
    if not token:
        print("❌ No API token found. Set WEATHERSIGHT_API_TOKEN environment variable.")
        return False

    mcp = WeatherSightMCP()

    # Test initialize endpoint
    test_request = {"method": "initialize"}
    result = mcp.handle_mcp_request(test_request)

    if "error" in result:
        print(f"❌ Connection failed: {result['error']['message']}")
        return False
    else:
        print("✅ Connection successful!")
        print(f"✅ Server: {result.get('serverInfo', {}).get('name', 'Unknown')}")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="WeatherSight MCP Client - Connect Claude to WeatherSight's weather APIs",
        epilog="For more information, visit: https://weathersight.io/docs",
    )
    parser.add_argument(
        "--configure",
        action="store_true",
        help="Show Claude Desktop configuration instructions",
    )
    parser.add_argument(
        "--test", action="store_true", help="Test connection to WeatherSight API"
    )
    parser.add_argument(
        "--version", action="version", version="WeatherSight MCP Client 1.0.0"
    )

    args = parser.parse_args()

    if args.configure:
        configure_claude_desktop()
        return

    if args.test:
        test_connection()
        return

    # Default: Run MCP server
    mcp = WeatherSightMCP()
    mcp.run_mcp_server()


if __name__ == "__main__":
    main()

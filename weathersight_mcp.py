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
        """Make request to WeatherSight MCP endpoint"""
        try:
            # Add API token to tool calls if available
            if endpoint == "/mcp/tools/call" and "params" in data:
                token = os.getenv("WEATHERSIGHT_API_TOKEN")
                if token and "arguments" in data["params"]:
                    if "token" not in data["params"]["arguments"]:
                        data["params"]["arguments"]["token"] = token

            response = self.session.post(
                f"{BASE_URL}{endpoint}",
                json=data,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "WeatherSight-MCP-Client/1.0.0",
                },
            )

            # Handle HTTP errors
            if not response.ok:
                return {
                    "jsonrpc": "2.0",
                    "id": data.get("id"),
                    "error": {
                        "code": -32603,
                        "message": f"HTTP {response.status_code}: {response.text}",
                    },
                }

            return response.json()

        except requests.exceptions.Timeout:
            return {
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Request timed out after {TIMEOUT} seconds",
                },
            }
        except requests.exceptions.RequestException as e:
            return {
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "error": {"code": -32603, "message": f"Request failed: {str(e)}"},
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "error": {"code": -32603, "message": f"Unexpected error: {str(e)}"},
            }

    def run_mcp_server(self):
        """Main MCP server loop - pure pass-through to production server"""
        try:
            for line in sys.stdin:
                try:
                    line = line.strip()
                    if not line:
                        continue

                    request = json.loads(line)
                    method = request.get("method", "")

                    # Map method to endpoint
                    if method == "initialize":
                        endpoint = "/mcp/initialize"
                    elif method == "tools/list":
                        endpoint = "/mcp/tools/list"
                    elif method == "tools/call":
                        endpoint = "/mcp/tools/call"
                    else:
                        # Unknown method - return error
                        response = {
                            "jsonrpc": "2.0",
                            "id": request.get("id"),
                            "error": {
                                "code": -32601,
                                "message": f"Unknown method: {method}",
                            },
                        }
                        print(json.dumps(response))
                        sys.stdout.flush()
                        continue

                    # Forward request to production server and return response
                    response = self.make_request(endpoint, request)
                    print(json.dumps(response))
                    sys.stdout.flush()

                except json.JSONDecodeError as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {"code": -32700, "message": f"Parse error: {str(e)}"},
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()

                except Exception as e:
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id") if "request" in locals() else None,
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}",
                        },
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()

        except KeyboardInterrupt:
            sys.exit(0)
        except Exception as e:
            print(f"Fatal error: {e}", file=sys.stderr)
            sys.exit(1)


def test_connection():
    """Test connection to WeatherSight API"""
    print("Testing connection to WeatherSight API...")

    token = os.getenv("WEATHERSIGHT_API_TOKEN")
    if not token:
        print("❌ No API token found. Set WEATHERSIGHT_API_TOKEN environment variable.")
        return False

    mcp = WeatherSightMCP()

    # Test initialize endpoint
    test_request = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    result = mcp.make_request("/mcp/initialize", test_request)

    if "error" in result:
        print(f"❌ Connection failed: {result['error']['message']}")
        return False
    else:
        print("✅ Connection successful!")
        if "result" in result:
            server_info = result["result"].get("serverInfo", {})
            print(f"✅ Server: {server_info.get('name', 'WeatherSight MCP')}")
        return True


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

    # Default: Run MCP server (pure pass-through mode)
    mcp = WeatherSightMCP()
    mcp.run_mcp_server()


if __name__ == "__main__":
    main()

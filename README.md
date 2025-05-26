# Weathersight MCP Client

Connect Claude Desktop to WeatherSight's professional weather APIs for advanced weather analysis, anomaly detection, and climatological insights.

## Features

🌡️ **Weather Anomalies** - Detect unusual weather patterns  
📊 **Climate Analysis** - Compare current conditions to historical baselines  
🔍 **Location Intelligence** - Detailed weather data for any location  
📈 **Weather Streaks** - Identify consecutive weather patterns  
🌍 **Global Coverage** - Worldwide weather data access  
⚡ **Fast & Reliable** - Optimized for Claude Desktop with 5-minute timeouts  

## Quick Start

### 1. Installation

```bash
pip install weathersight-mcp
```

### 2. Get API Token

Sign up at [weathersight.io](https://weathersight.io/signup) to get your free API token.

### 3. Configure Claude Desktop

Run the configuration helper:

```bash
weathersight-mcp --configure
```

This will show you exactly what to add to your Claude Desktop config file.

### 4. Test Connection

```bash
export WEATHERSIGHT_API_TOKEN="your_token_here"
weathersight-mcp --test
```

### 5. Restart Claude Desktop

After updating the config, restart Claude Desktop to load the WeatherSight tools.

## Usage Examples

Once configured, ask Claude questions like:

- **"What weather anomalies occurred in Chicago during January 2024?"**
- **"Compare this winter's temperature in New York to the historical average"**
- **"Show me the longest heat streak in Phoenix last summer"**
- **"Get typical weather patterns for London in March"**
- **"What are the current degree days for heating in Boston?"**

## Configuration

### Manual Configuration

Add this to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`  
**Linux**: `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "weathersight": {
      "command": "weathersight-mcp",
      "args": [],
      "env": {
        "WEATHERSIGHT_API_TOKEN": "your_actual_token_here"
      }
    }
  }
}
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `WEATHERSIGHT_API_TOKEN` | Your API token from weathersight.io | Yes |

## Available Tools

The MCP client provides access to these WeatherSight APIs:

- **location** - Get location information and coordinates
- **typicalweather** - Climatological weather patterns
- **anomalies** - Weather anomaly detection
- **streaks** - Consecutive weather pattern analysis
- **compare** - Compare weather periods
- **timeseries** - Historical weather time series
- **degreedays** - Heating/cooling degree day calculations
- **metrics** - Available weather parameters
- **countries** - Country weather information

## Troubleshooting

### Connection Issues

```bash
# Test your connection
weathersight-mcp --test

# Check if token is set
echo $WEATHERSIGHT_API_TOKEN
```

### Timeout Issues

The client is configured with generous timeouts:
- **Connection timeout**: 30 seconds
- **Request timeout**: 5 minutes (300 seconds)
- **Auto-retry**: 3 attempts with backoff

### Common Issues

**"No API token found"**
- Set the `WEATHERSIGHT_API_TOKEN` environment variable
- Or add it to your Claude Desktop config

**"Authentication failed"**
- Check your token is correct
- Verify your account is active at weathersight.io

**"Rate limit exceeded"**
- Wait a moment and try again
- Consider upgrading your API plan

## Support

- **Documentation**: [weathersight.io/docs](https://weathersight.io/docs)
- **API Reference**: [weathersight.io/docs](https://weathersight.io/docs)
- **Issues**: [GitHub Issues](https://github.com/weathersight/weathersight-mcp/issues)
- **Email**: contact@weathersight.io

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions welcome! Please read our contributing guidelines and submit pull requests to our GitHub repository.

---

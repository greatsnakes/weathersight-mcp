# Weathersight MCP Connector

Connect Claude — or any MCP client — to [Weathersight](https://weathersight.io): 100+ years
of station observations, typical-weather climatology, anomalies, extremes, degree days, and
long-term climate trends for locations worldwide.

This is a **remote MCP server**. There is nothing to install.

```
https://weathersight.io/api/mcp
```

## Connect

**Claude (Desktop or web)**

1. Settings → Connectors → **Add custom connector**
2. URL: `https://weathersight.io/api/mcp`
3. **Connect**, then sign in when prompted

Signing in creates your Weathersight API token automatically if you don't already have one,
and starts a free trial. Existing token holders keep the token they already have.

**Other MCP clients**

Point the client at the same URL. The server speaks Streamable HTTP (spec 2025-03-26) and
authenticates with OAuth 2.0 authorization-code + PKCE, including dynamic client
registration — no manual credential setup.

## What you can ask

- *"What's the typical weather in Reykjavik in late September?"*
- *"Has Bengaluru's monsoon onset shifted over the last 40 years?"*
- *"Which US cities broke heat records last week?"*
- *"Compare this July in Madrid to its 1991–2020 baseline."*

## Managing your connection

- **Your token and plan:** https://weathersight.io/subscription
- **API reference:** https://weathersight.io/docs

If the connector stops returning data, your client will usually prompt you to sign in again.
If it reports that your plan has lapsed, visit the subscription page above — the connector
and token resume working once a plan is active.

## About this repository

This repo is the public home of Weathersight's [MCP Registry](https://registry.modelcontextprotocol.io)
entry. [`server.json`](server.json) is the metadata record that tells the registry — and the
directories that mirror it — what this server is called, where it lives, and how to reach it.

The connector itself is served from the Weathersight application.

## License

MIT — see [LICENSE](LICENSE).

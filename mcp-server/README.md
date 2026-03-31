# NEPSE Intelligence Docker MCP Server

**Model Context Protocol (MCP) server** for NEPSE Intelligence that exposes Docker container management and market data query tools.

Allows external applications (Claude, your own services, etc.) to:
- List, inspect, start/stop/restart Docker containers
- Query NEPSE market data (live, historical, indices, signals)
- Manage NEPSE Intelligence services

## What is MCP?

[Model Context Protocol](https://modelcontextprotocol.io) is an open standard that lets AI models and applications safely interact with tools and data sources. Think of it as a standardized way to expose capabilities via a tool interface.

## Features

**Docker Management Tools**
- `list_containers` - List running/stopped containers
- `inspect_container` - Get detailed container info
- `get_container_logs` - View container logs
- `start_container`, `stop_container`, `restart_container` - Control containers

**NEPSE Market Data Tools**
- `get_live_market` - Real-time market data from NEPSE API
- `get_stock` - Stock details by symbol
- `get_index` - Index data (NEPSE, Banking, Hydro, etc.)
- `get_market_history` - Historical price data (24h, 72h, 30d, etc.)
- `get_top_gainers`, `get_top_losers` - Performance rankings
- `get_market_summary` - Overall market stats

## Quick Start

### Local Development

```bash
cd mcp-server

# Install dependencies
pip install -r requirements.txt

# Run MCP server (listens on stdin/stdout)
python nepse_docker_mcp.py
```

The server will start and listen for MCP protocol messages on stdin/stdout.

### Docker Deployment

```bash
# Build MCP container
docker build -t nepse-mcp:latest .

# Run with Docker socket access (allows container management)
docker run -v /var/run/docker.sock:/var/run/docker.sock nepse-mcp:latest

# Or with network access to backend API
docker run -e NEPSE_DB_API=http://backend:8000 nepse-mcp:latest
```

### Integration with Claude (GitHub Copilot CLI)

Add to your `.github/copilot-instructions.md`:

```markdown
## Available MCP Server

I have access to a Docker MCP server running locally that can:
- List and manage Docker containers
- Query NEPSE market data and historical prices

Use these tools to help with container orchestration and market analysis.
```

Then configure in Copilot CLI:

```bash
copilot /mcp
# Follow prompts to add the MCP server
```

Or directly in `~/.copilot/copilot-instructions.md`:

```json
{
  "mcpServers": {
    "nepse-docker": {
      "command": "python",
      "args": ["/path/to/nepse_docker_mcp.py"],
      "description": "NEPSE market data and Docker container management"
    }
  }
}
```

## Tool Specifications

### Docker Management

#### `list_containers`
Lists all Docker containers.

**Input:**
```json
{
  "all": false  // Include stopped containers (default: false)
}
```

**Output:**
```json
[
  {
    "id": "abc123def456",
    "name": "nepse_backend",
    "image": "nepse-intelligence-backend:latest",
    "status": "running",
    "ports": {"8000/tcp": [{"HostIp": "0.0.0.0", "HostPort": "8000"}]}
  }
]
```

#### `inspect_container`
Get detailed info about a container.

**Input:**
```json
{
  "container_id": "nepse_backend"
}
```

**Output:**
```json
{
  "id": "abc123def456",
  "name": "nepse_backend",
  "status": "running",
  "image": "nepse-intelligence-backend:latest",
  "created": "2026-03-31T16:00:00.000000Z",
  "ports": {...},
  "env": [...],
  "mounts": [...]
}
```

#### `get_container_logs`
Get logs from a container.

**Input:**
```json
{
  "container_id": "nepse_backend",
  "lines": 50
}
```

**Output:** Last 50 lines of container logs (text)

#### `start_container`, `stop_container`, `restart_container`
Control container state.

**Input:**
```json
{
  "container_id": "nepse_backend"
}
```

### Market Data Queries

#### `get_live_market`
Real-time NEPSE market snapshot.

**Output:**
```json
{
  "data": [
    {
      "symbol": "NABIL",
      "companyName": "Nabil Bank Limited",
      "ltp": 1234.50,
      "change": 12.50,
      "percentChange": 1.02,
      "volume": 50000
    }
  ]
}
```

#### `get_stock`
Get stock details from database.

**Input:**
```json
{
  "symbol": "NABIL"
}
```

**Output:**
```json
{
  "symbol": "NABIL",
  "name": "Nabil Bank Limited",
  "sector": "Banking",
  "current_price": 1234.50,
  "open_price": 1225.00,
  "high_price": 1240.00,
  "low_price": 1220.00,
  "volume": 50000,
  "market_cap": 12345678900.00,
  "updated_at": "2026-03-31T16:45:00Z"
}
```

#### `get_market_history`
Historical price data for technical analysis.

**Input:**
```json
{
  "symbol": "NABIL",
  "hours": 24,
  "limit": 100
}
```

**Output:**
```json
[
  {
    "price": 1234.50,
    "volume": 5000,
    "timestamp": "2026-03-31T16:40:00Z"
  }
]
```

#### `get_top_gainers` / `get_top_losers`
Performance rankings.

**Input:**
```json
{
  "limit": 10
}
```

#### `get_market_summary`
Overall market stats.

**Output:**
```json
{
  "total_stocks": 245,
  "total_indices": 12,
  "last_stock_update": "2026-03-31T16:45:00Z",
  "last_index_update": "2026-03-31T16:45:00Z"
}
```

## Environment Variables

```env
# MCP Server
NEPSE_DB_API=http://localhost:8000       # Backend API endpoint
NEPSE_API=https://nepseapi.surajrimal.dev  # Live market API

# Docker
DOCKER_HOST=unix:///var/run/docker.sock  # Docker daemon socket
```

## Architecture

```
External App (Claude, Python service, etc.)
        ↓
    MCP Protocol (stdio)
        ↓
NEPSE Docker MCP Server
        ↓
    ┌───┴───┐
    ↓       ↓
Docker   NEPSE API
Client   Backend
```

## Use Cases

1. **Container Orchestration via AI**
   - "List NEPSE services"
   - "Restart the database container"
   - "Check backend logs for errors"

2. **Market Analysis via AI**
   - "What were the top 5 gainers today?"
   - "Show me NABIL price history"
   - "Is the market bullish or bearish?"

3. **Automated Monitoring**
   - AI agent monitors containers and alerts on failures
   - Auto-restart failed services
   - Track market anomalies

## Security Considerations

⚠️ **Important**: The MCP server has full Docker access. Treat it as having root privileges.

**Best practices:**
1. Only expose MCP over trusted networks
2. Use Docker socket permissions carefully (run as non-root if possible)
3. Validate all inputs (container IDs, stock symbols)
4. Rate-limit API calls to prevent abuse
5. Consider running in a sandboxed environment

## Development

Run tests:
```bash
# Coming in Phase 2
```

Format code:
```bash
black nepse_docker_mcp.py
```

## Future Enhancements

- WebSocket support for real-time updates
- Streaming tool results for large datasets
- Batch operations (get multiple stocks in one call)
- Portfolio tracking and alerts
- ML-powered signal generation
- Persistent session state

## Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check documentation in main README.md
- Review SECURITY.md for security practices

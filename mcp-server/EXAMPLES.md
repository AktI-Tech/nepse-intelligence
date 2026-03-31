# MCP Integration Examples

## Example 1: Using with GitHub Copilot CLI

### Step 1: Configure MCP Server

Create `~/.copilot/copilot-instructions.md`:

```markdown
# NEPSE Intelligence MCP Server

I have access to a Docker MCP server that provides:

## Docker Container Management
- List containers: `list_containers`
- Inspect containers: `inspect_container` 
- Get logs: `get_container_logs`
- Control containers: `start_container`, `stop_container`, `restart_container`

## NEPSE Market Data
- Live market data: `get_live_market`
- Stock details: `get_stock`
- Price history: `get_market_history`
- Top gainers/losers: `get_top_gainers`, `get_top_losers`
- Market summary: `get_market_summary`

Use these tools to help with Docker operations and market analysis.
```

### Step 2: Run MCP Server

```bash
cd /path/to/nepse-intelligence/mcp-server
python nepse_docker_mcp.py
```

### Step 3: Use in Copilot

```bash
copilot
> @mcp list the NEPSE services running in Docker
> @mcp show me NABIL stock price history for the last 24 hours
> @mcp restart the backend container if it's unhealthy
```

---

## Example 2: Python Application Integration

```python
import json
import subprocess
from typing import Any

class NEPSEMCPClient:
    def __init__(self, mcp_script_path: str):
        self.mcp_script = mcp_script_path
    
    def call_tool(self, tool_name: str, **kwargs) -> Any:
        """Call an MCP tool."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": kwargs
            }
        }
        
        result = subprocess.run(
            ["python", self.mcp_script],
            input=json.dumps(request).encode(),
            capture_output=True
        )
        
        return json.loads(result.stdout)
    
    def get_stock(self, symbol: str) -> dict:
        return self.call_tool("get_stock", symbol=symbol)
    
    def list_containers(self) -> list:
        return self.call_tool("list_containers", all=False)


# Usage
client = NEPSEMCPClient("/path/to/nepse_docker_mcp.py")

# Get stock data
nabil = client.get_stock("NABIL")
print(f"NABIL price: {nabil['current_price']}")

# List containers
containers = client.list_containers()
for c in containers:
    print(f"Container: {c['name']} ({c['status']})")
```

---

## Example 3: Node.js Integration

```javascript
// nepse-mcp-client.js
const { spawn } = require('child_process');

class NEPSEMCPClient {
  constructor(mcpScriptPath) {
    this.mcpScriptPath = mcpScriptPath;
  }

  async callTool(toolName, args = {}) {
    const request = {
      jsonrpc: '2.0',
      id: 1,
      method: 'tools/call',
      params: {
        name: toolName,
        arguments: args
      }
    };

    return new Promise((resolve, reject) => {
      const process = spawn('python', [this.mcpScriptPath]);
      
      let stdout = '';
      process.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      process.on('close', (code) => {
        try {
          resolve(JSON.parse(stdout));
        } catch (e) {
          reject(e);
        }
      });

      process.stdin.write(JSON.stringify(request));
      process.stdin.end();
    });
  }

  async getStock(symbol) {
    return this.callTool('get_stock', { symbol });
  }

  async getMarketSummary() {
    return this.callTool('get_market_summary');
  }
}

// Usage
const client = new NEPSEMCPClient('/path/to/nepse_docker_mcp.py');

client.getStock('NABIL').then(stock => {
  console.log(`NABIL: ${stock.current_price}`);
});
```

---

## Example 4: Docker Compose with MCP

Add to your `docker-compose.yml`:

```yaml
  mcp-server:
    build: ./mcp-server
    container_name: nepse_mcp
    depends_on:
      - backend
      - db
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - NEPSE_DB_API=http://backend:8000
      - NEPSE_API=https://nepseapi.surajrimal.dev
    restart: unless-stopped
```

Then run:
```bash
docker compose up --build
```

---

## Example 5: Real-World Use Case - Market Monitoring

```python
#!/usr/bin/env python3
"""Monitor NEPSE market and restart services on anomalies."""

import json
import subprocess
import time
from typing import Any

class MarketMonitor:
    def __init__(self, mcp_path: str):
        self.mcp_path = mcp_path
    
    def call_mcp(self, tool: str, **kwargs) -> Any:
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": tool, "arguments": kwargs}
        }
        result = subprocess.run(
            ["python", self.mcp_path],
            input=json.dumps(request).encode(),
            capture_output=True
        )
        return json.loads(result.stdout)
    
    def monitor_loop(self, interval: int = 300):
        """Monitor market every 5 minutes."""
        while True:
            try:
                # Get market summary
                summary = self.call_mcp("get_market_summary")
                print(f"[{time.ctime()}] Market data updated at {summary['last_stock_update']}")
                
                # Check containers
                containers = self.call_mcp("list_containers")
                for c in containers:
                    if c['status'] != 'running':
                        print(f"⚠️  Container {c['name']} is {c['status']}")
                        # Auto-restart if needed
                        self.call_mcp("restart_container", container_id=c['id'])
                
                # Get top gainers
                gainers = self.call_mcp("get_top_gainers", limit=5)
                print(f"📈 Top gainers: {[s['symbol'] for s in gainers]}")
                
            except Exception as e:
                print(f"Error: {e}")
            
            time.sleep(interval)

# Run monitor
monitor = MarketMonitor("/path/to/nepse_docker_mcp.py")
monitor.monitor_loop()
```

---

## Troubleshooting

**Q: "Container not found" error**  
A: Use container name (e.g., "nepse_backend") or full ID. Get list with `list_containers`.

**Q: "Error fetching stock" from MCP**  
A: Check backend is running: `GET http://localhost:8000/health`

**Q: MCP server won't start**  
A: Install dependencies: `pip install -r mcp-server/requirements.txt`

**Q: Docker socket permission denied**  
A: Run as correct user or use `sudo`

---

## Further Reading

- [MCP Specification](https://modelcontextprotocol.io)
- [Docker Python SDK](https://docker-py.readthedocs.io)
- [GitHub Copilot MCP Integration](https://docs.github.com/copilot)

#!/usr/bin/env python3
"""NEPSE Intelligence Docker MCP Server

Exposes Docker container management and NEPSE market data via MCP protocol.
Allows external apps to query market data and manage containers.
"""

import os
import json
import logging
from typing import Any
import docker
import requests
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, ToolResult
import mcp.server.stdio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
docker_client = docker.from_env()
NEPSE_API = "https://nepseapi.surajrimal.dev"
NEPSE_DB_API = "http://localhost:8000"  # Local backend

# Server instance
server = mcp.server.stdio.StdioServer()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available MCP tools."""
    return [
        Tool(
            name="list_containers",
            description="List all Docker containers with status",
            inputSchema={
                "type": "object",
                "properties": {
                    "all": {
                        "type": "boolean",
                        "description": "Include stopped containers (default: false)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="inspect_container",
            description="Get detailed info about a specific container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_id": {"type": "string", "description": "Container ID or name"}
                },
                "required": ["container_id"]
            }
        ),
        Tool(
            name="get_container_logs",
            description="Get logs from a container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_id": {"type": "string", "description": "Container ID or name"},
                    "lines": {"type": "integer", "description": "Last N lines (default: 50)"}
                },
                "required": ["container_id"]
            }
        ),
        Tool(
            name="start_container",
            description="Start a stopped container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_id": {"type": "string", "description": "Container ID or name"}
                },
                "required": ["container_id"]
            }
        ),
        Tool(
            name="stop_container",
            description="Stop a running container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_id": {"type": "string", "description": "Container ID or name"}
                },
                "required": ["container_id"]
            }
        ),
        Tool(
            name="restart_container",
            description="Restart a container",
            inputSchema={
                "type": "object",
                "properties": {
                    "container_id": {"type": "string", "description": "Container ID or name"}
                },
                "required": ["container_id"]
            }
        ),
        Tool(
            name="get_live_market",
            description="Get live NEPSE market data",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_stock",
            description="Get stock details and price",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol (e.g., NABIL)"}
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_index",
            description="Get NEPSE index details",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Index symbol (e.g., NEPSE)"}
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_market_history",
            description="Get historical market data for a stock",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "Stock symbol"},
                    "hours": {"type": "integer", "description": "Hours back (default: 24)"},
                    "limit": {"type": "integer", "description": "Max records (default: 100)"}
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_top_gainers",
            description="Get top gaining stocks",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of results (default: 10)"}
                },
                "required": []
            }
        ),
        Tool(
            name="get_top_losers",
            description="Get top losing stocks",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {"type": "integer", "description": "Number of results (default: 10)"}
                },
                "required": []
            }
        ),
        Tool(
            name="get_market_summary",
            description="Get market summary (total stocks, last update)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> ToolResult:
    """Handle tool calls."""
    try:
        if name == "list_containers":
            return await handle_list_containers(arguments)
        elif name == "inspect_container":
            return await handle_inspect_container(arguments)
        elif name == "get_container_logs":
            return await handle_get_logs(arguments)
        elif name == "start_container":
            return await handle_start_container(arguments)
        elif name == "stop_container":
            return await handle_stop_container(arguments)
        elif name == "restart_container":
            return await handle_restart_container(arguments)
        elif name == "get_live_market":
            return await handle_get_live_market(arguments)
        elif name == "get_stock":
            return await handle_get_stock(arguments)
        elif name == "get_index":
            return await handle_get_index(arguments)
        elif name == "get_market_history":
            return await handle_get_market_history(arguments)
        elif name == "get_top_gainers":
            return await handle_get_top_gainers(arguments)
        elif name == "get_top_losers":
            return await handle_get_top_losers(arguments)
        elif name == "get_market_summary":
            return await handle_get_market_summary(arguments)
        else:
            return ToolResult(content=[TextContent(type="text", text=f"Unknown tool: {name}")])
    except Exception as e:
        logger.error(f"Error calling tool {name}: {e}")
        return ToolResult(content=[TextContent(type="text", text=f"Error: {str(e)}")])


# Docker Management Handlers
async def handle_list_containers(args: dict) -> ToolResult:
    """List containers."""
    all_containers = args.get("all", False)
    containers = docker_client.containers.list(all=all_containers)
    
    result = []
    for container in containers:
        result.append({
            "id": container.id[:12],
            "name": container.name,
            "image": container.image.tags[0] if container.image.tags else container.image.id[:12],
            "status": container.status,
            "ports": container.ports
        })
    
    return ToolResult(content=[TextContent(type="text", text=json.dumps(result, indent=2))])


async def handle_inspect_container(args: dict) -> ToolResult:
    """Inspect a container."""
    container_id = args.get("container_id")
    try:
        container = docker_client.containers.get(container_id)
        info = {
            "id": container.id[:12],
            "name": container.name,
            "status": container.status,
            "image": container.image.tags[0] if container.image.tags else container.image.id[:12],
            "created": str(container.attrs["Created"]),
            "ports": container.ports,
            "env": container.attrs["Config"]["Env"],
            "mounts": [{m["Source"]: m["Destination"]} for m in container.attrs["Mounts"]]
        }
        return ToolResult(content=[TextContent(type="text", text=json.dumps(info, indent=2))])
    except docker.errors.NotFound:
        return ToolResult(content=[TextContent(type="text", text=f"Container not found: {container_id}")])


async def handle_get_logs(args: dict) -> ToolResult:
    """Get container logs."""
    container_id = args.get("container_id")
    lines = args.get("lines", 50)
    try:
        container = docker_client.containers.get(container_id)
        logs = container.logs(tail=lines).decode('utf-8')
        return ToolResult(content=[TextContent(type="text", text=logs)])
    except docker.errors.NotFound:
        return ToolResult(content=[TextContent(type="text", text=f"Container not found: {container_id}")])


async def handle_start_container(args: dict) -> ToolResult:
    """Start a container."""
    container_id = args.get("container_id")
    try:
        container = docker_client.containers.get(container_id)
        container.start()
        return ToolResult(content=[TextContent(type="text", text=f"Started container: {container_id}")])
    except docker.errors.NotFound:
        return ToolResult(content=[TextContent(type="text", text=f"Container not found: {container_id}")])


async def handle_stop_container(args: dict) -> ToolResult:
    """Stop a container."""
    container_id = args.get("container_id")
    try:
        container = docker_client.containers.get(container_id)
        container.stop()
        return ToolResult(content=[TextContent(type="text", text=f"Stopped container: {container_id}")])
    except docker.errors.NotFound:
        return ToolResult(content=[TextContent(type="text", text=f"Container not found: {container_id}")])


async def handle_restart_container(args: dict) -> ToolResult:
    """Restart a container."""
    container_id = args.get("container_id")
    try:
        container = docker_client.containers.get(container_id)
        container.restart()
        return ToolResult(content=[TextContent(type="text", text=f"Restarted container: {container_id}")])
    except docker.errors.NotFound:
        return ToolResult(content=[TextContent(type="text", text=f"Container not found: {container_id}")])


# NEPSE Market Data Handlers
async def handle_get_live_market(args: dict) -> ToolResult:
    """Get live market data."""
    try:
        r = requests.get(f"{NEPSE_API}/LiveMarket", timeout=10)
        r.raise_for_status()
        data = r.json()
        return ToolResult(content=[TextContent(type="text", text=json.dumps(data, indent=2))])
    except Exception as e:
        return ToolResult(content=[TextContent(type="text", text=f"Error fetching live market: {str(e)}")])


async def handle_get_stock(args: dict) -> ToolResult:
    """Get stock details."""
    symbol = args.get("symbol")
    try:
        r = requests.get(f"{NEPSE_DB_API}/api/stocks/{symbol}", timeout=10)
        r.raise_for_status()
        data = r.json()
        return ToolResult(content=[TextContent(type="text", text=json.dumps(data, indent=2))])
    except Exception as e:
        return ToolResult(content=[TextContent(type="text", text=f"Error fetching stock {symbol}: {str(e)}")])


async def handle_get_index(args: dict) -> ToolResult:
    """Get index details."""
    symbol = args.get("symbol")
    try:
        r = requests.get(f"{NEPSE_DB_API}/api/indices/{symbol}", timeout=10)
        r.raise_for_status()
        data = r.json()
        return ToolResult(content=[TextContent(type="text", text=json.dumps(data, indent=2))])
    except Exception as e:
        return ToolResult(content=[TextContent(type="text", text=f"Error fetching index {symbol}: {str(e)}")])


async def handle_get_market_history(args: dict) -> ToolResult:
    """Get market history."""
    symbol = args.get("symbol")
    hours = args.get("hours", 24)
    limit = args.get("limit", 100)
    try:
        r = requests.get(
            f"{NEPSE_DB_API}/api/stocks/{symbol}/history?hours={hours}&limit={limit}",
            timeout=10
        )
        r.raise_for_status()
        data = r.json()
        return ToolResult(content=[TextContent(type="text", text=json.dumps(data, indent=2))])
    except Exception as e:
        return ToolResult(content=[TextContent(type="text", text=f"Error fetching history for {symbol}: {str(e)}")])


async def handle_get_top_gainers(args: dict) -> ToolResult:
    """Get top gainers."""
    limit = args.get("limit", 10)
    try:
        r = requests.get(f"{NEPSE_DB_API}/api/market/top-gainers?limit={limit}", timeout=10)
        r.raise_for_status()
        data = r.json()
        return ToolResult(content=[TextContent(type="text", text=json.dumps(data, indent=2))])
    except Exception as e:
        return ToolResult(content=[TextContent(type="text", text=f"Error fetching gainers: {str(e)}")])


async def handle_get_top_losers(args: dict) -> ToolResult:
    """Get top losers."""
    limit = args.get("limit", 10)
    try:
        r = requests.get(f"{NEPSE_DB_API}/api/market/top-losers?limit={limit}", timeout=10)
        r.raise_for_status()
        data = r.json()
        return ToolResult(content=[TextContent(type="text", text=json.dumps(data, indent=2))])
    except Exception as e:
        return ToolResult(content=[TextContent(type="text", text=f"Error fetching losers: {str(e)}")])


async def handle_get_market_summary(args: dict) -> ToolResult:
    """Get market summary."""
    try:
        r = requests.get(f"{NEPSE_DB_API}/api/market/summary", timeout=10)
        r.raise_for_status()
        data = r.json()
        return ToolResult(content=[TextContent(type="text", text=json.dumps(data, indent=2))])
    except Exception as e:
        return ToolResult(content=[TextContent(type="text", text=f"Error fetching summary: {str(e)}")])


async def main():
    """Run the MCP server."""
    logger.info("Starting NEPSE Intelligence Docker MCP Server")
    await server.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

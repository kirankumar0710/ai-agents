# custom_mcp_server.py

# TESTING THIS SERVER
# ─────────────────────────────────────────────────────────────
# custom_mcp_server.py  ← your code, pure Python
#         ↑
# MCP Inspector         ← dev-only tool (Node.js), not part of your stack
#
# Install once:  brew install node   (Mac)  /  sudo apt install nodejs npm
# Run:           npx @modelcontextprotocol/inspector python custom_mcp_server.py
#
# Same idea as Postman for REST APIs — throwaway test UI, not production.
# ─────────────────────────────────────────────────────────────


from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

import json
import httpx
import asyncio

from tools import weather
from tools import calculator as calc
from tools import websearch

# Initialize MCP server
app = Server("my-custom-agent-tools")


# ── Tool 1: Web Search ──────────────────────────────────
@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """Tell clients what tools this server offers"""
    return [
        types.Tool(
            name="web_search",
            description="Search the web for current information",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "max_results": {
                        "type": "integer",
                        "description": "Max results to return",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="calculate",
            description="Perform mathematical calculations",
            inputSchema={
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Math expression to evaluate, e.g. '2 + 2 * 10'",
                    }
                },
                "required": ["expression"],
            },
        ),
        types.Tool(
            name="get_weather",
            description="Get current weather for a city",
            inputSchema={
                "type": "object",
                "properties": {"city": {"type": "string", "description": "City name"}},
                "required": ["city"],
            },
        ),
    ]


# ── Tool Execution ──────────────────────────────────────
@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Execute a tool and return results"""

    if name == "web_search":
        query = arguments["query"]
        output = websearch.web_search(query)
        return [types.TextContent(type="text", text=output)]

    elif name == "calculate":
        expression = arguments["expression"]
        result = calc.calculator(expression)
        return [types.TextContent(type="text", text=f"{expression} = {result}")]

    elif name == "get_weather":
        city = arguments["city"]
        city_weather = weather.get_weather(city)
        return [types.TextContent(type="text", text=city_weather)]

    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


# ── Run the server ──────────────────────────────────────
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())

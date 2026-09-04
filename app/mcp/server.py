from __future__ import annotations

from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP


mcp = FastMCP(
    name="ADK-Ollama-AgentHub-MCP",
    instructions="Local MCP server for ADK-Ollama-AgentHub.",
    host="127.0.0.1",
    port=8000,
    streamable_http_path="/mcp",
)


@mcp.tool()
def mcp_health() -> dict[str, str]:
    """Return the health status of the MCP server."""
    return {
        "status": "healthy",
        "server": "ADK-Ollama-AgentHub-MCP",
    }


@mcp.tool()
def get_server_time() -> str:
    """Return the current UTC time from the MCP server."""
    return datetime.now(timezone.utc).isoformat()


@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


@mcp.tool()
def multiply_numbers(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
    )
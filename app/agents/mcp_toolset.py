from __future__ import annotations

from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset,
    StreamableHTTPConnectionParams,
)


mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="http://127.0.0.1:8000/mcp",
        headers={
            "Accept": "application/json, text/event-stream",
        },
        timeout=5.0,
        sse_read_timeout=300.0,
        terminate_on_close=True,
    ),
    tool_name_prefix="mcp_",
    require_confirmation=False,
    use_mcp_resources=False,
)


__all__ = ["mcp_toolset"]
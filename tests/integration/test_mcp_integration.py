from __future__ import annotations

import pytest

from app.agents.root_agent import mcp_toolset


@pytest.mark.anyio
async def test_mcp_toolset_discovers_server_tools():
    tools = await mcp_toolset.get_tools()

    tool_names = {tool.name for tool in tools}

    assert "mcp_health" in tool_names
    assert "get_server_time" in tool_names
    assert "add_numbers" in tool_names
    assert "multiply_numbers" in tool_names
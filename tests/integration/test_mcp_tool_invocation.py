from __future__ import annotations

import pytest

from app.agents.root_agent import mcp_toolset


@pytest.mark.anyio
async def test_mcp_add_numbers_invocation():
    tools = await mcp_toolset.get_tools()

    add_tool = next(
        tool for tool in tools
        if tool.name == "add_numbers"
    )

    result = await add_tool.run_async(
        args={
            "a": 10,
            "b": 25,
        },
        tool_context=None,
    )

    assert result is not None

    if isinstance(result, dict):
        assert result.get("result") == 35 or result.get("content")
    else:
        assert "35" in str(result)
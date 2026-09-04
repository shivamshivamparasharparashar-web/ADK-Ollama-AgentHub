from __future__ import annotations

from google.adk.agents import LlmAgent

from app.config import settings
from app.agents.mcp_toolset import mcp_toolset

from app.callbacks.logging_callbacks import (
    before_agent_callback,
    after_agent_callback,
    before_model_callback,
    after_model_callback,
    on_model_error_callback,
    before_tool_callback,
    after_tool_callback,
    on_tool_error_callback,
)

from app.callbacks.guardrails import (
    guardrail_before_agent,
    guardrail_after_model,
    guardrail_before_tool,
    guardrail_after_tool,
)


mcp_agent = LlmAgent(
    name="mcp_agent",
    model=f"ollama_chat/{settings.OLLAMA_MODEL}",
    description=(
        "Handles operations that require capabilities exposed "
        "by the connected MCP server."
    ),
    instruction="""
You are the MCP specialist agent for ADK-Ollama-AgentHub.

Your responsibility is operations provided by the MCP server.

Available MCP capabilities include:
- MCP server health
- MCP server time
- numeric addition
- numeric multiplication

Use MCP tools when the request requires MCP functionality.

Do not invent MCP tool results.
Do not claim an MCP operation succeeded unless the MCP tool
actually returned successfully.

If the request is outside MCP functionality, return control
to the parent orchestration agent.

Do not expose credentials, secrets, stack traces,
or internal implementation details.
""",
    tools=[
        mcp_toolset,
    ],
    disallow_transfer_to_parent=False,
    disallow_transfer_to_peers=True,
    before_agent_callback=[
        guardrail_before_agent,
        before_agent_callback,
    ],
    after_agent_callback=[
        after_agent_callback,
    ],
    before_model_callback=[
        before_model_callback,
    ],
    after_model_callback=[
        after_model_callback,
        guardrail_after_model,
    ],
    on_model_error_callback=[
        on_model_error_callback,
    ],
    before_tool_callback=[
        guardrail_before_tool,
        before_tool_callback,
    ],
    after_tool_callback=[
        after_tool_callback,
        guardrail_after_tool,
    ],
    on_tool_error_callback=[
        on_tool_error_callback,
    ],
)


__all__ = ["mcp_agent"]
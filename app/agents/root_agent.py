from __future__ import annotations

from google.adk.agents import LlmAgent

from app.config import settings

from app.agents.sub_agents.general_agent import general_agent
from app.agents.sub_agents.api_agent import api_agent
from app.agents.sub_agents.mcp_agent import mcp_agent
from app.agents.mcp_toolset import mcp_toolset

from app.callbacks.logging_callbacks import (
    before_agent_callback,
    after_agent_callback,
    before_model_callback,
    after_model_callback,
    on_model_error_callback,
)

from app.callbacks.guardrails import (
    guardrail_before_agent,
    guardrail_after_model,
)


# ---------------------------------------------------------------------------
# Root Orchestrator
# ---------------------------------------------------------------------------

root_agent = LlmAgent(
    name="root_agent",
    model=f"ollama_chat/{settings.OLLAMA_MODEL}",
    description=(
        "Primary orchestration agent for ADK-Ollama-AgentHub. "
        "Routes requests to the appropriate specialized agent."
    ),
    instruction="""
You are the primary orchestration agent for ADK-Ollama-AgentHub.

Your responsibility is to understand the user's request and delegate
it to the appropriate specialist agent.

Available specialist agents:

1. general_agent
   Handles:
   - General questions
   - Mathematical calculations
   - System status
   - Current date/time

2. api_agent
   Handles:
   - HTTP/API operations
   - Requests requiring the api_request tool

3. mcp_agent
   Handles:
   - MCP server operations
   - MCP server health
   - MCP server time
   - Numeric addition
   - Numeric multiplication

Delegation rules:
- Delegate general/local utility requests to general_agent.
- Delegate HTTP/API requests to api_agent.
- Delegate MCP requests to mcp_agent.
- Do not invent tool results.
- Do not claim an operation succeeded unless the delegated agent
  actually completed it successfully.
- Do not expose credentials, secrets, stack traces,
  or internal implementation details.
- If a request is ambiguous, determine the most appropriate
  specialist before proceeding.
""",
    sub_agents=[
        general_agent,
        api_agent,
        mcp_agent,
    ],
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
)


__all__ = [
    "root_agent",
    "mcp_toolset",
]
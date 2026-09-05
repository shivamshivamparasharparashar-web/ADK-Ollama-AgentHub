from __future__ import annotations

from datetime import datetime, timezone

from litellm import acompletion
from mcp.server.fastmcp import FastMCP

from app.config import settings


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


@mcp.tool()
async def ask_question(question: str) -> dict[str, str]:
    """Answer a question independently using the configured Ollama LLM."""
    if not question.strip():
        raise ValueError("question must not be empty.")

    response = await acompletion(
        model=f"ollama_chat/{settings.OLLAMA_MODEL}",
        messages=[
            {
                "role": "user",
                "content": question,
            }
        ],
        api_base=settings.OLLAMA_API_BASE,
    )

    answer = response.choices[0].message.content

    if not answer:
        raise RuntimeError("The LLM returned an empty response.")

    return {
        "question": question,
        "answer": answer,
        "model": settings.OLLAMA_MODEL,
    }


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
    )
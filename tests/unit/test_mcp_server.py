from __future__ import annotations

from datetime import datetime

from app.mcp.server import (
    add_numbers,
    get_server_time,
    mcp_health,
    multiply_numbers,
)


def test_mcp_health():
    result = mcp_health()

    assert isinstance(result, dict)
    assert result["status"] == "healthy"
    assert result["server"] == "ADK-Ollama-AgentHub-MCP"


def test_get_server_time():
    result = get_server_time()

    assert isinstance(result, str)

    parsed = datetime.fromisoformat(result)

    assert parsed.tzinfo is not None
    assert parsed.utcoffset() is not None


def test_add_numbers():
    assert add_numbers(2, 3) == 5


def test_add_numbers_with_decimals():
    result = add_numbers(2.5, 3.75)

    assert result == 6.25


def test_multiply_numbers():
    assert multiply_numbers(4, 5) == 20


def test_multiply_numbers_with_decimals():
    result = multiply_numbers(2.5, 4)

    assert result == 10.0
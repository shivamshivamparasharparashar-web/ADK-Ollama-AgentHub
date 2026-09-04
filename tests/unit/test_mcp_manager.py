from __future__ import annotations

import pytest

from app.errors import ConfigurationError, ToolExecutionError
from app.mcp.mcp_config import (
    MCPConnectionConfig,
    MCPServerConfig,
)
from app.mcp.mcp_manager import MCPManager


def test_stdio_configuration_is_valid():
    config = MCPConnectionConfig(
        transport="stdio",
        command="python",
        args=("-m", "example_server"),
    )

    config.validate()


def test_streamable_http_configuration_is_valid():
    config = MCPConnectionConfig(
        transport="streamable_http",
        url="https://example.com/mcp",
        headers={
            "Accept": "application/json",
        },
    )

    config.validate()


def test_sse_configuration_is_valid():
    config = MCPConnectionConfig(
        transport="sse",
        url="https://example.com/sse",
    )

    config.validate()


def test_invalid_transport_is_rejected():
    config = MCPConnectionConfig(
        transport="invalid",
    )

    with pytest.raises(ConfigurationError):
        config.validate()


def test_stdio_requires_command():
    config = MCPConnectionConfig(
        transport="stdio",
    )

    with pytest.raises(ConfigurationError):
        config.validate()


def test_http_requires_url():
    config = MCPConnectionConfig(
        transport="streamable_http",
    )

    with pytest.raises(ConfigurationError):
        config.validate()


def test_http_rejects_non_http_url():
    config = MCPConnectionConfig(
        transport="streamable_http",
        url="ftp://example.com/mcp",
    )

    with pytest.raises(ConfigurationError):
        config.validate()


def test_invalid_timeout_is_rejected():
    config = MCPConnectionConfig(
        transport="stdio",
        command="python",
        timeout=0,
    )

    with pytest.raises(ConfigurationError):
        config.validate()


def test_invalid_headers_are_rejected():
    config = MCPConnectionConfig(
        transport="streamable_http",
        url="https://example.com/mcp",
        headers={
            "Authorization": 123,
        },
    )

    with pytest.raises(ConfigurationError):
        config.validate()


def test_invalid_environment_variables_are_rejected():
    config = MCPConnectionConfig(
        transport="stdio",
        command="python",
        env={
            "TEST": 123,
        },
    )

    with pytest.raises(ConfigurationError):
        config.validate()


def test_server_configuration_is_valid():
    config = MCPServerConfig(
        name="test_server",
        connection=MCPConnectionConfig(
            transport="stdio",
            command="python",
        ),
        tool_filter=(
            "tool_a",
            "tool_b",
        ),
        tool_name_prefix="test_",
    )

    config.validate()


def test_empty_server_name_is_rejected():
    config = MCPServerConfig(
        name="",
        connection=MCPConnectionConfig(
            transport="stdio",
            command="python",
        ),
    )

    with pytest.raises(ConfigurationError):
        config.validate()


def test_empty_tool_filter_entry_is_rejected():
    config = MCPServerConfig(
        name="test",
        connection=MCPConnectionConfig(
            transport="stdio",
            command="python",
        ),
        tool_filter=(
            "valid_tool",
            "",
        ),
    )

    with pytest.raises(ConfigurationError):
        config.validate()


def test_empty_tool_prefix_is_rejected():
    config = MCPServerConfig(
        name="test",
        connection=MCPConnectionConfig(
            transport="stdio",
            command="python",
        ),
        tool_name_prefix=" ",
    )

    with pytest.raises(ConfigurationError):
        config.validate()


def test_negative_cache_ttl_is_rejected():
    config = MCPServerConfig(
        name="test",
        connection=MCPConnectionConfig(
            transport="stdio",
            command="python",
        ),
        tool_list_cache_ttl_seconds=-1,
    )

    with pytest.raises(ConfigurationError):
        config.validate()


def test_manager_starts_empty():
    manager = MCPManager()

    assert manager.get_toolsets() == []


def test_manager_get_missing_toolset_returns_none():
    manager = MCPManager()

    assert manager.get_toolset("missing") is None


def test_manager_builds_stdio_connection():
    manager = MCPManager()

    config = MCPConnectionConfig(
        transport="stdio",
        command="python",
        args=("-m", "example_server"),
        timeout=10,
    )

    connection = manager._build_connection(config)

    assert connection.server_params.command == "python"
    assert connection.server_params.args == [
        "-m",
        "example_server",
    ]
    assert connection.timeout == 10


def test_manager_builds_streamable_http_connection():
    manager = MCPManager()

    config = MCPConnectionConfig(
        transport="streamable_http",
        url="https://example.com/mcp",
        headers={
            "Authorization": "Bearer test",
        },
        timeout=10,
        sse_read_timeout=120,
        terminate_on_close=False,
    )

    connection = manager._build_connection(config)

    assert connection.url == "https://example.com/mcp"
    assert connection.headers == {
        "Authorization": "Bearer test",
    }
    assert connection.timeout == 10
    assert connection.sse_read_timeout == 120
    assert connection.terminate_on_close is False


def test_manager_builds_sse_connection():
    manager = MCPManager()

    config = MCPConnectionConfig(
        transport="sse",
        url="https://example.com/sse",
        headers={
            "Authorization": "Bearer test",
        },
        timeout=10,
    )

    connection = manager._build_connection(config)

    assert connection.url == "https://example.com/sse"
    assert connection.headers == {
        "Authorization": "Bearer test",
    }
    assert connection.timeout == 10


def test_duplicate_server_registration_is_rejected():
    manager = MCPManager()

    config = MCPServerConfig(
        name="test",
        connection=MCPConnectionConfig(
            transport="stdio",
            command="python",
        ),
    )

    first = manager.create_toolset(config)

    assert first is manager.get_toolset("test")

    with pytest.raises(ConfigurationError):
        manager.create_toolset(config)


@pytest.mark.anyio
async def test_remove_toolset():
    manager = MCPManager()

    config = MCPServerConfig(
        name="test",
        connection=MCPConnectionConfig(
            transport="stdio",
            command="python",
        ),
    )

    manager.create_toolset(config)

    removed = manager.remove_toolset("test")

    assert removed is not None
    assert manager.get_toolset("test") is None


def test_toolset_creation_normalizes_unexpected_errors(monkeypatch):
    manager = MCPManager()

    config = MCPServerConfig(
        name="test",
        connection=MCPConnectionConfig(
            transport="stdio",
            command="python",
        ),
    )

    def fail(_config):
        raise RuntimeError("internal MCP failure")

    monkeypatch.setattr(
        manager,
        "_build_connection",
        fail,
    )

    with pytest.raises(ToolExecutionError) as exc_info:
        manager.create_toolset(config)

    assert str(exc_info.value) == "MCP toolset creation failed."
    assert exc_info.value.details == "RuntimeError"
    assert "internal MCP failure" not in str(exc_info.value)
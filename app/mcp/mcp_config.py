from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.errors import ConfigurationError


SUPPORTED_TRANSPORTS = {
    "stdio",
    "sse",
    "streamable_http",
}


@dataclass(frozen=True, slots=True)
class MCPConnectionConfig:
    """Connection configuration for an MCP server."""

    transport: str

    # STDIO configuration
    command: str | None = None
    args: tuple[str, ...] = ()
    env: dict[str, str] | None = None
    cwd: str | Path | None = None

    # HTTP/SSE configuration
    url: str | None = None
    headers: dict[str, Any] | None = None

    # Connection timeout
    timeout: float = 5.0

    # Streamable HTTP specific settings
    sse_read_timeout: float = 300.0
    terminate_on_close: bool = True

    def validate(self) -> None:
        """Validate MCP connection configuration."""

        if self.transport not in SUPPORTED_TRANSPORTS:
            raise ConfigurationError(
                "MCP transport must be one of: "
                + ", ".join(sorted(SUPPORTED_TRANSPORTS))
            )

        if self.timeout <= 0:
            raise ConfigurationError(
                "MCP connection timeout must be greater than zero."
            )

        if self.transport == "stdio":
            if not self.command or not self.command.strip():
                raise ConfigurationError(
                    "MCP STDIO configuration requires a command."
                )

            if self.url is not None:
                raise ConfigurationError(
                    "MCP STDIO configuration must not define a URL."
                )

        else:
            if not self.url or not self.url.strip():
                raise ConfigurationError(
                    "MCP HTTP/SSE configuration requires a URL."
                )

            if not (
                self.url.startswith("http://")
                or self.url.startswith("https://")
            ):
                raise ConfigurationError(
                    "MCP server URL must use HTTP or HTTPS."
                )

            if self.command is not None:
                raise ConfigurationError(
                    "MCP HTTP/SSE configuration must not define a command."
                )

        if self.headers is not None:
            if not isinstance(self.headers, dict):
                raise ConfigurationError(
                    "MCP headers must be a dictionary."
                )

            for name, value in self.headers.items():
                if not isinstance(name, str) or not name.strip():
                    raise ConfigurationError(
                        "MCP header names must be non-empty strings."
                    )

                if not isinstance(value, str):
                    raise ConfigurationError(
                        "MCP header values must be strings."
                    )

        if self.env is not None:
            if not isinstance(self.env, dict):
                raise ConfigurationError(
                    "MCP environment variables must be a dictionary."
                )

            for name, value in self.env.items():
                if not isinstance(name, str) or not name.strip():
                    raise ConfigurationError(
                        "MCP environment variable names must be non-empty strings."
                    )

                if not isinstance(value, str):
                    raise ConfigurationError(
                        "MCP environment variable values must be strings."
                    )


@dataclass(frozen=True, slots=True)
class MCPServerConfig:
    """Complete configuration for one MCP server."""

    name: str
    connection: MCPConnectionConfig

    tool_filter: tuple[str, ...] | None = None
    tool_name_prefix: str | None = None

    require_confirmation: bool = False
    use_mcp_resources: bool = False

    tool_list_cache_ttl_seconds: float | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        """Validate the complete MCP server configuration."""

        if not self.name.strip():
            raise ConfigurationError(
                "MCP server name must not be empty."
            )

        self.connection.validate()

        if self.tool_filter is not None:
            for tool_name in self.tool_filter:
                if not isinstance(tool_name, str) or not tool_name.strip():
                    raise ConfigurationError(
                        "MCP tool filter entries must be non-empty strings."
                    )

        if self.tool_name_prefix is not None:
            if not self.tool_name_prefix.strip():
                raise ConfigurationError(
                    "MCP tool name prefix must not be empty."
                )

        if self.tool_list_cache_ttl_seconds is not None:
            if self.tool_list_cache_ttl_seconds < 0:
                raise ConfigurationError(
                    "MCP tool-list cache TTL must not be negative."
                )


__all__ = [
    "MCPConnectionConfig",
    "MCPServerConfig",
    "SUPPORTED_TRANSPORTS",
]
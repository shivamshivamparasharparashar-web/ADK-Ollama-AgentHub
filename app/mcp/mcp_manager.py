from __future__ import annotations

from typing import Any

from app.errors import ConfigurationError, ToolExecutionError
from app.mcp.mcp_config import (
    MCPConnectionConfig,
    MCPServerConfig,
)

from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset,
    SseConnectionParams,
    StdioConnectionParams,
    StdioServerParameters,
    StreamableHTTPConnectionParams,
)


class MCPManager:
    """Application-level manager for ADK MCP toolsets."""

    def __init__(self) -> None:
        self._toolsets: dict[str, McpToolset] = {}

    @staticmethod
    def _build_connection(
        config: MCPConnectionConfig,
    ) -> Any:
        """Build the ADK MCP connection parameters."""

        config.validate()

        if config.transport == "stdio":
            server_params = StdioServerParameters(
                command=config.command,
                args=list(config.args),
                env=dict(config.env) if config.env else None,
                cwd=config.cwd,
            )

            return StdioConnectionParams(
                server_params=server_params,
                timeout=config.timeout,
            )

        if config.transport == "sse":
            kwargs: dict[str, Any] = {
                "url": config.url,
            }

            if config.headers:
                kwargs["headers"] = dict(config.headers)

            if config.timeout is not None:
                kwargs["timeout"] = config.timeout

            return SseConnectionParams(**kwargs)

        if config.transport == "streamable_http":
            kwargs = {
                "url": config.url,
                "timeout": config.timeout,
                "sse_read_timeout": config.sse_read_timeout,
                "terminate_on_close": config.terminate_on_close,
            }

            if config.headers:
                kwargs["headers"] = dict(config.headers)

            return StreamableHTTPConnectionParams(**kwargs)

        raise ConfigurationError(
            f"Unsupported MCP transport: {config.transport}"
        )

    def create_toolset(
        self,
        server_config: MCPServerConfig,
    ) -> McpToolset:
        """Create and register an ADK MCP toolset."""

        try:
            server_config.validate()

            if server_config.name in self._toolsets:
                raise ConfigurationError(
                    f"MCP server '{server_config.name}' is already registered."
                )

            connection = self._build_connection(
                server_config.connection
            )

            toolset = McpToolset(
                connection_params=connection,
                tool_filter=(
                    list(server_config.tool_filter)
                    if server_config.tool_filter is not None
                    else None
                ),
                tool_name_prefix=server_config.tool_name_prefix,
                tool_list_cache_ttl_seconds=(
                    server_config.tool_list_cache_ttl_seconds
                ),
                require_confirmation=server_config.require_confirmation,
                use_mcp_resources=server_config.use_mcp_resources,
            )

            self._toolsets[server_config.name] = toolset

            return toolset

        except ConfigurationError:
            raise

        except Exception as exc:
            raise ToolExecutionError(
                "MCP toolset creation failed.",
                details=type(exc).__name__,
            ) from exc

    def get_toolset(
        self,
        server_name: str,
    ) -> McpToolset | None:
        """Return a registered MCP toolset."""

        return self._toolsets.get(server_name)

    def get_toolsets(self) -> list[McpToolset]:
        """Return all registered MCP toolsets."""

        return list(self._toolsets.values())

    def remove_toolset(
        self,
        server_name: str,
    ) -> McpToolset | None:
        """Remove a registered toolset without closing it."""

        return self._toolsets.pop(server_name, None)

    async def close_toolset(
        self,
        server_name: str,
    ) -> None:
        """Close and remove one MCP toolset."""

        toolset = self._toolsets.pop(server_name, None)

        if toolset is None:
            return

        try:
            await toolset.close()
        except Exception as exc:
            raise ToolExecutionError(
                "MCP toolset cleanup failed.",
                details=type(exc).__name__,
            ) from exc

    async def close_all(self) -> None:
        """Close all registered MCP toolsets."""

        toolsets = list(self._toolsets.items())
        self._toolsets.clear()

        failures: list[str] = []

        for server_name, toolset in toolsets:
            try:
                await toolset.close()
            except Exception as exc:
                failures.append(
                    f"{server_name}:{type(exc).__name__}"
                )

        if failures:
            raise ToolExecutionError(
                "MCP toolset cleanup failed.",
                details=",".join(failures),
            )


mcp_manager = MCPManager()


__all__ = [
    "MCPManager",
    "mcp_manager",
]
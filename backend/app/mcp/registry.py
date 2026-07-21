from __future__ import annotations

from typing import Any, Protocol

from app.mcp.schemas import MCPToolDefinition


class MCPToolProtocol(Protocol):
    name: str
    description: str
    input_schema: dict[str, Any]
    requires_approval: bool

    async def execute(
        self,
        arguments: dict[str, Any],
    ) -> Any:
        ...


class MCPToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, MCPToolProtocol] = {}

    def register(
        self,
        tool: MCPToolProtocol,
        *,
        replace: bool = True,
    ) -> MCPToolProtocol:
        normalized_name = tool.name.strip().lower()

        if not normalized_name:
            raise ValueError("Tool name cannot be empty.")

        if normalized_name in self._tools and not replace:
            raise ValueError(
                f"MCP tool '{normalized_name}' is already registered."
            )

        self._tools[normalized_name] = tool
        return tool

    def unregister(self, tool_name: str) -> bool:
        normalized_name = tool_name.strip().lower()
        return self._tools.pop(normalized_name, None) is not None

    def get(self, tool_name: str) -> MCPToolProtocol:
        normalized_name = tool_name.strip().lower()
        tool = self._tools.get(normalized_name)

        if tool is None:
            raise KeyError(
                f"MCP tool '{tool_name}' is not registered."
            )

        return tool

    def exists(self, tool_name: str) -> bool:
        return tool_name.strip().lower() in self._tools

    def list(self) -> list[MCPToolProtocol]:
        return list(self._tools.values())

    def definitions(self) -> list[MCPToolDefinition]:
        return [
            MCPToolDefinition(
                name=tool.name,
                description=tool.description,
                input_schema=tool.input_schema,
                requires_approval=tool.requires_approval,
            )
            for tool in self.list()
        ]

    def clear(self) -> None:
        self._tools.clear()


mcp_tool_registry = MCPToolRegistry()
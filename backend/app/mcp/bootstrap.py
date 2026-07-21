from __future__ import annotations

from app.mcp.registry import (
    MCPToolRegistry,
    mcp_tool_registry,
)
from app.mcp.tools import (
    CalculatorTool,
    CurrentTimeTool,
    EchoTool,
)


def register_default_tools(
    registry: MCPToolRegistry | None = None,
) -> MCPToolRegistry:
    selected_registry = registry or mcp_tool_registry

    for tool in (
        EchoTool(),
        CurrentTimeTool(),
        CalculatorTool(),
    ):
        selected_registry.register(
            tool,
            replace=True,
        )

    return selected_registry
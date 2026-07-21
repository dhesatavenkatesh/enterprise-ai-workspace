from __future__ import annotations

import asyncio
from time import perf_counter
from typing import Any

from app.mcp.bootstrap import register_default_tools
from app.mcp.registry import (
    MCPToolRegistry,
    mcp_tool_registry,
)
from app.mcp.schemas import MCPToolCallResult


class MCPExecutor:
    def __init__(
        self,
        registry: MCPToolRegistry | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.registry = registry or mcp_tool_registry
        self.timeout_seconds = timeout_seconds

        register_default_tools(self.registry)

    async def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any] | None = None,
    ) -> MCPToolCallResult:
        start_time = perf_counter()

        try:
            tool = self.registry.get(tool_name)

        except KeyError as exc:
            return MCPToolCallResult(
                tool_name=tool_name,
                success=False,
                error=str(exc),
                execution_time_ms=self._elapsed_ms(start_time),
            )

        if tool.requires_approval:
            return MCPToolCallResult(
                tool_name=tool.name,
                success=False,
                error="This tool requires human approval.",
                requires_approval=True,
                execution_time_ms=self._elapsed_ms(start_time),
            )

        try:
            result = await asyncio.wait_for(
                tool.execute(arguments or {}),
                timeout=self.timeout_seconds,
            )

            return MCPToolCallResult(
                tool_name=tool.name,
                success=True,
                result=result,
                execution_time_ms=self._elapsed_ms(start_time),
            )

        except TimeoutError:
            return MCPToolCallResult(
                tool_name=tool.name,
                success=False,
                error=(
                    f"Tool execution exceeded "
                    f"{self.timeout_seconds} seconds."
                ),
                execution_time_ms=self._elapsed_ms(start_time),
            )

        except Exception as exc:
            return MCPToolCallResult(
                tool_name=tool.name,
                success=False,
                error=str(exc),
                execution_time_ms=self._elapsed_ms(start_time),
            )

    @staticmethod
    def _elapsed_ms(start_time: float) -> float:
        return round(
            (perf_counter() - start_time) * 1000,
            2,
        )
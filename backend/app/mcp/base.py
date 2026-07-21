from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.mcp.schemas import MCPToolDefinition


class BaseMCPTool(ABC):
    definition: MCPToolDefinition

    @abstractmethod
    async def execute(self, arguments: dict[str, Any]) -> Any:
        raise NotImplementedError

    def validate_arguments(self, arguments: dict[str, Any]) -> None:
        missing = [
            parameter.name
            for parameter in self.definition.parameters
            if parameter.required and parameter.name not in arguments
        ]
        if missing:
            raise ValueError(f"Missing required arguments: {', '.join(missing)}")

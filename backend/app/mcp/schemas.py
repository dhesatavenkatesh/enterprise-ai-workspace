from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class MCPToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any] = Field(default_factory=dict)
    requires_approval: bool = False


class MCPToolCallRequest(BaseModel):
    tool_name: str = Field(
        min_length=1,
        max_length=100,
    )
    arguments: dict[str, Any] = Field(default_factory=dict)
    conversation_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class MCPToolCallResult(BaseModel):
    tool_name: str
    success: bool
    result: Any | None = None
    error: str | None = None
    requires_approval: bool = False
    execution_time_ms: float = 0.0
    executed_at: datetime = Field(default_factory=utc_now)


class MCPHealthResponse(BaseModel):
    status: str
    registered_tools: int
    tool_names: list[str]
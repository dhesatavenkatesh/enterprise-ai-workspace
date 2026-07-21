from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    TIMEOUT = "timeout"


class AgentRequest(BaseModel):
    message: str = Field(min_length=1)
    user_id: str | int | None = None
    conversation_id: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    agent_name: str
    status: AgentStatus
    content: str = ""
    provider: str | None = None
    model: str | None = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentDefinition(BaseModel):
    name: str
    description: str
    capabilities: list[str]
    supported_tools: list[str]

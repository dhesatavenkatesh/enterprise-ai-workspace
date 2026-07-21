from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from app.agents.schemas import AgentResponse


class OrchestrationMode(str, Enum):
    AUTO = "auto"
    SINGLE = "single"
    MULTI = "multi"


class OrchestratorRequest(BaseModel):
    message: str = Field(min_length=1, max_length=20000)
    agent_name: str | None = None
    agent_names: list[str] = Field(default_factory=list)
    conversation_id: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("agent_names")
    @classmethod
    def remove_duplicate_agents(cls, values: list[str]) -> list[str]:
        return list(dict.fromkeys(name.strip() for name in values if name.strip()))


class RoutingDecision(BaseModel):
    selected_agents: list[str]
    reason: str
    confidence: float = Field(ge=0.0, le=1.0)


class OrchestratorResponse(BaseModel):
    orchestration_id: str = Field(default_factory=lambda: str(uuid4()))
    mode: OrchestrationMode
    routing: RoutingDecision
    results: list[AgentResponse]
    final_answer: str
    successful_agents: int = 0
    failed_agents: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

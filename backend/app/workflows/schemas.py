from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator


def utc_now() -> datetime:
    return datetime.now(UTC)


class WorkflowStepType(StrEnum):
    AGENT = "agent"
    MCP_TOOL = "mcp_tool"


class WorkflowStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    DISABLED = "disabled"


class WorkflowRunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


class WorkflowStepDefinition(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = Field(min_length=1, max_length=120)
    type: WorkflowStepType
    target: str = Field(min_length=1, max_length=120)
    input_template: str = Field(default="{input}", min_length=1, max_length=20000)
    arguments: dict[str, Any] = Field(default_factory=dict)
    continue_on_error: bool = False
    requires_approval: bool = False
    approval_reason: str | None = Field(default=None, max_length=1000)


class WorkflowCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str = Field(default="", max_length=1000)
    steps: list[WorkflowStepDefinition] = Field(min_length=1, max_length=30)
    status: WorkflowStatus = WorkflowStatus.ACTIVE

    @field_validator("steps")
    @classmethod
    def unique_step_names(cls, steps: list[WorkflowStepDefinition]):
        names = [step.name.strip().lower() for step in steps]
        if len(names) != len(set(names)):
            raise ValueError("Workflow step names must be unique.")
        return steps


class WorkflowDefinition(WorkflowCreate):
    id: str = Field(default_factory=lambda: str(uuid4()))
    owner_id: int | str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class WorkflowRunRequest(BaseModel):
    input: str = Field(min_length=1, max_length=20000)
    context: dict[str, Any] = Field(default_factory=dict)
    conversation_id: str | None = None


class WorkflowStepResult(BaseModel):
    step_id: str
    step_name: str
    type: WorkflowStepType
    target: str
    success: bool
    output: Any | None = None
    error: str | None = None
    started_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime = Field(default_factory=utc_now)


class WorkflowRunResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    workflow_id: str
    workflow_name: str
    status: WorkflowRunStatus = WorkflowRunStatus.PENDING
    initial_input: str
    context: dict[str, Any] = Field(default_factory=dict)
    conversation_id: str | None = None
    final_output: Any | None = None
    error: str | None = None
    step_results: list[WorkflowStepResult] = Field(default_factory=list)
    current_step_index: int = 0
    pending_approval_id: str | None = None
    started_at: datetime = Field(default_factory=utc_now)
    completed_at: datetime | None = None

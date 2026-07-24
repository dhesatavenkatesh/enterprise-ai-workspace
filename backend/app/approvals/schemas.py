from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ApprovalCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2000)
    resource_type: str = Field(min_length=1, max_length=80)
    resource_id: str = Field(min_length=1, max_length=200)
    requested_by: int | str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class ApprovalRequest(ApprovalCreate):
    id: str = Field(default_factory=lambda: str(uuid4()))
    status: ApprovalStatus = ApprovalStatus.PENDING
    decided_by: int | str | None = None
    decision_comment: str | None = None
    created_at: datetime = Field(default_factory=utc_now)
    decided_at: datetime | None = None


class ApprovalDecision(BaseModel):
    comment: str | None = Field(default=None, max_length=1000)


class ApprovalListResponse(BaseModel):
    total: int
    items: list[ApprovalRequest]

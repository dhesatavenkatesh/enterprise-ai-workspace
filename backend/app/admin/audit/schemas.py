from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AdminAuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None = None
    action: str
    resource: str | None = None
    resource_id: str | None = None
    ip_address: str | None = None
    details: str | None = None
    created_at: datetime


class AdminAuditLogListResponse(BaseModel):
    items: list[AdminAuditLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AuditLogCreate(BaseModel):
    user_id: int | None = None

    action: str = Field(
        min_length=1,
        max_length=100,
    )

    resource: str | None = Field(
        default=None,
        max_length=100,
    )

    resource_id: str | None = Field(
        default=None,
        max_length=100,
    )

    ip_address: str | None = Field(
        default=None,
        max_length=45,
    )

    details: dict[str, Any] | str | None = None

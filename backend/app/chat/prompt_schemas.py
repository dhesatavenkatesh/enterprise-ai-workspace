from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.chat.models import PromptStatus


class PromptTemplateCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150,
        examples=["Python Code Reviewer"],
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
        examples=["Reviews Python code and suggests improvements."],
    )

    content: str = Field(
        min_length=3,
        examples=[
            "Review the following Python code and provide improvements:\n\n{code}"
        ],
    )

    category: str | None = Field(
        default=None,
        max_length=100,
        examples=["development"],
    )

    status: PromptStatus = PromptStatus.ACTIVE

    is_public: bool = False


class PromptTemplateUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
    )

    description: str | None = Field(
        default=None,
        max_length=1000,
    )

    content: str | None = Field(
        default=None,
        min_length=3,
    )

    category: str | None = Field(
        default=None,
        max_length=100,
    )

    status: PromptStatus | None = None

    is_public: bool | None = None


class PromptTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: int | None
    name: str
    description: str | None
    content: str
    category: str | None
    status: PromptStatus
    is_public: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime


class PromptTemplateListResponse(BaseModel):
    items: list[PromptTemplateResponse]
    total: int
    page: int
    page_size: int


class PromptTemplateDeleteResponse(BaseModel):
    message: str
    template_id: UUID


class PromptTemplateUseResponse(BaseModel):
    message: str
    template_id: UUID
    usage_count: int
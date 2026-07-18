from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    prompt: str = Field(
        min_length=1,
        max_length=20_000,
    )

    conversation_id: UUID | None = None
    template_id: UUID | None = None

    system_prompt: str | None = None
    provider: str | None = None
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = None
    
    provider: Literal[
        "groq",
        "openai",
        "ollama",
    ] | None = None

    model: str | None = Field(
        default=None,
        max_length=100,
    )

    system_prompt: str | None = Field(
        default=None,
        max_length=10_000,
    )

    temperature: float | None = Field(
        default=None,
        ge=0,
        le=2,
    )

    max_tokens: int | None = Field(
        default=None,
        ge=1,
        le=32_768,
    )


class ChatResponse(BaseModel):
    conversation_id: UUID
    response: str
    tokens: int
    prompt_tokens: int = 0
    completion_tokens: int = 0
    provider: str
    model: str


class RenameConversationRequest(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=255,
    )


class MessageResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    conversation_id: UUID
    role: str
    content: str
    token_count: int
    prompt_tokens: int
    completion_tokens: int
    provider: str | None
    model_name: str | None
    rating: int | None
    created_at: datetime


class ConversationSummaryResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    title: str
    is_archived: bool
    is_pinned: bool
    created_at: datetime
    updated_at: datetime


class ConversationDetailResponse(
    ConversationSummaryResponse
):
    messages: list[MessageResponse]


class ConversationHistoryResponse(BaseModel):
    items: list[ConversationSummaryResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class DeleteConversationResponse(BaseModel):
    message: str
    conversation_id: UUID
from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """Request body sent by frontend/src/services/chatService.ts."""

    message: str = Field(
        min_length=1,
        max_length=20_000,
    )

    conversation_id: UUID | None = None
    prompt_template_id: UUID | None = None

    provider: (
        Literal[
            "groq",
            "openai",
            "ollama",
        ]
        | None
    ) = None

    model_name: str | None = Field(
        default=None,
        max_length=100,
    )

    temperature: float = Field(
        default=0.7,
        ge=0,
        le=2,
    )

    max_tokens: int | None = Field(
        default=None,
        ge=1,
        le=32_768,
    )

    system_prompt: str | None = Field(
        default=None,
        max_length=10_000,
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
    )

    document_id: UUID | None = None

    department: str | None = Field(
        default=None,
        max_length=100,
    )

    document_type: str | None = Field(
        default=None,
        max_length=100,
    )

    minimum_similarity: float = Field(
        default=0.1,
        ge=0.0,
        le=1.0,
    )

    # Compatibility properties for the existing Sprint 2 backend.
    @property
    def prompt(self) -> str:
        return self.message

    @property
    def template_id(self) -> UUID | None:
        return self.prompt_template_id

    @property
    def model(self) -> str | None:
        return self.model_name


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
    rating: int | None = None
    created_at: datetime


class ChatResponse(BaseModel):
    conversation_id: UUID
    conversation_title: str
    user_message: MessageResponse
    assistant_message: MessageResponse
    total_tokens: int = 0


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


class ConversationDetailResponse(ConversationSummaryResponse):
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

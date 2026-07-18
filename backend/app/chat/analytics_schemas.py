from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class ProviderUsage(BaseModel):
    provider: str
    message_count: int
    total_tokens: int


class ModelUsage(BaseModel):
    model: str
    provider: str | None = None
    message_count: int
    total_tokens: int


class DailyChatActivity(BaseModel):
    activity_date: date
    conversations: int
    messages: int
    total_tokens: int


class ChatAnalyticsSummaryResponse(BaseModel):
    total_conversations: int
    active_conversations: int
    archived_conversations: int

    total_messages: int
    user_messages: int
    assistant_messages: int
    system_messages: int

    total_tokens: int
    prompt_tokens: int
    completion_tokens: int

    most_used_provider: str | None = None
    most_used_model: str | None = None

    average_messages_per_conversation: float
    average_tokens_per_conversation: float


class ChatUsageAnalyticsResponse(BaseModel):
    days: int = Field(ge=1, le=365)
    providers: list[ProviderUsage]
    models: list[ModelUsage]
    daily_activity: list[DailyChatActivity]
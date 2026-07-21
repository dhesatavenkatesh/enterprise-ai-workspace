from __future__ import annotations

from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class DocumentChunkCreate(BaseModel):
    document_id: UUID

    chunk_number: int = Field(
        ...,
        ge=0,
    )

    chunk_text: str = Field(
        ...,
        min_length=1,
    )

    page_number: int | None = Field(
        default=None,
        ge=1,
    )

    section: str | None = Field(
        default=None,
        max_length=255,
    )

    chunk_size: int | None = Field(
        default=None,
        ge=1,
    )

    chunk_overlap: int | None = Field(
        default=None,
        ge=0,
    )

    embedding_model: str | None = Field(
        default=None,
        max_length=255,
    )

    vector_dimension: int | None = Field(
        default=None,
        ge=1,
    )

    vector_id: str | None = Field(
        default=None,
        max_length=255,
    )

    token_count: int | None = Field(
        default=None,
        ge=0,
    )

    processing_time_ms: float | None = Field(
        default=None,
        ge=0,
    )

    metadata: dict = Field(
        default_factory=dict,
    )


class DocumentChunkResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: UUID
    document_id: UUID

    chunk_number: int
    chunk_text: str

    page_number: int | None
    section: str | None

    chunk_size: int | None
    chunk_overlap: int | None

    embedding_model: str | None
    vector_dimension: int | None
    vector_id: str | None

    token_count: int | None
    processing_time_ms: float | None

    chunk_metadata: dict

    is_deleted: bool


class DocumentChunkListResponse(BaseModel):
    items: list[DocumentChunkResponse]
    total: int
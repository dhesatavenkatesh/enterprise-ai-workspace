from __future__ import annotations

from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


# =============================================================================
# Shared schemas
# =============================================================================


class RAGBaseSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
    )


class RAGCitationResponse(RAGBaseSchema):
    citation_number: int
    document_id: str
    document_title: str
    file_name: str
    chunk_index: int
    content: str
    similarity: float
    department: str | None = None
    page_number: int | None = None


# =============================================================================
# Document indexing schemas
# =============================================================================


class DocumentIndexRequest(RAGBaseSchema):
    chunk_size: int = Field(
        default=512,
        ge=100,
        le=4000,
        description=(
            "Maximum size of each generated document chunk."
        ),
    )

    chunk_overlap: int = Field(
        default=50,
        ge=0,
        le=1000,
        description=(
            "Number of overlapping characters or tokens "
            "between consecutive chunks."
        ),
    )

    replace_existing: bool = Field(
        default=True,
        description=(
            "Delete and replace an existing document index."
        ),
    )

    @model_validator(mode="after")
    def validate_chunk_configuration(
        self,
    ) -> "DocumentIndexRequest":
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size."
            )

        return self


class DocumentIndexResponse(RAGBaseSchema):
    document_id: str
    status: str
    chunks_created: int
    vectors_stored: int
    embedding_model: str
    embedding_dimension: int
    processed_at: str


class DocumentIndexStatusResponse(RAGBaseSchema):
    document_id: str
    status: str
    processing_progress: int
    chunk_count: int
    embedding_model: str | None = None
    vector_dimension: int | None = None
    vector_collection: str | None = None
    indexed: bool


class DocumentIndexDeleteResponse(RAGBaseSchema):
    document_id: str
    vectors_deleted: int
    database_chunks_deleted: int
    status: str


# =============================================================================
# Search schemas
# =============================================================================


class RAGSearchRequest(RAGBaseSchema):
    query: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="Question or semantic search query.",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Maximum number of retrieved chunks.",
    )

    document_id: UUID | None = Field(
        default=None,
        description=(
            "Optionally restrict search to one document."
        ),
    )

    department: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    document_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    minimum_similarity: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description=(
            "Minimum similarity score required for a result."
        ),
    )


class RAGSearchResponse(RAGBaseSchema):
    query: str
    results: list[dict[str, Any]]
    citations: list[RAGCitationResponse]
    result_count: int
    search_time_ms: float


# =============================================================================
# Chat schemas
# =============================================================================


class RAGChatRequest(RAGBaseSchema):
    query: str = Field(
        ...,
        min_length=1,
        max_length=4000,
        description="Question to answer using indexed documents.",
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
    )

    document_id: UUID | None = None

    department: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    document_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    minimum_similarity: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
    )


class RAGChatResponse(RAGBaseSchema):
    query: str
    answer: str
    citations: list[RAGCitationResponse]
    sources_used: int
    context: str
    search_time_ms: float


# =============================================================================
# Analytics schemas
# =============================================================================


class RAGDocumentAnalytics(RAGBaseSchema):
    total: int
    indexed: int
    processing: int
    failed: int
    chunks: int


class RAGSearchAnalytics(RAGBaseSchema):
    total: int
    average_search_time_ms: float
    average_result_count: float


class RAGAnalyticsResponse(RAGBaseSchema):
    documents: RAGDocumentAnalytics
    searches: RAGSearchAnalytics
    vector_store: dict[str, Any]
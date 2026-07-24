from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class DocumentBase(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    document_type: str = Field(
        ...,
        min_length=1,
        max_length=50,
    )

    department: str | None = Field(
        default=None,
        max_length=100,
    )

    description: str | None = None


class DocumentCreate(DocumentBase):
    """
    Metadata received together with the uploaded file.
    """

    pass


class DocumentUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    document_type: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
    )

    department: str | None = Field(
        default=None,
        max_length=100,
    )

    description: str | None = None


class DocumentResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    user_id: int

    title: str
    file_name: str
    original_file_name: str | None

    document_type: str
    department: str | None
    description: str | None

    file_size: int
    file_path: str
    file_hash: str | None

    status: str
    version_number: int
    processing_progress: int
    chunk_count: int

    embedding_model: str | None
    vector_dimension: int | None
    vector_collection: str | None

    is_deleted: bool

    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None


class DocumentUploadResponse(BaseModel):
    message: str
    document: DocumentResponse


class DocumentListResponse(BaseModel):
    items: list[DocumentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class DocumentStatusResponse(BaseModel):
    id: UUID
    status: str
    processing_progress: int
    chunk_count: int
    embedding_model: str | None
    vector_dimension: int | None
    vector_collection: str | None


class DocumentDeleteResponse(BaseModel):
    message: str
    document_id: UUID

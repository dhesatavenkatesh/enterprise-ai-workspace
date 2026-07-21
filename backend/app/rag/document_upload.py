from __future__ import annotations

import hashlib
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.document import Document


logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

BASE_DIR = Path(__file__).resolve().parents[2]

UPLOAD_DIRECTORY = Path(
    os.getenv(
        "DOCUMENT_UPLOAD_DIRECTORY",
        str(BASE_DIR / "uploads" / "documents"),
    )
)

UPLOAD_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)


MAX_FILE_SIZE_MB = int(
    os.getenv(
        "DOCUMENT_MAX_FILE_SIZE_MB",
        "25",
    )
)

MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".md",
    ".doc",
    ".docx",
    ".csv",
    ".json",
}


# These values should match the PostgreSQL chk_documents_type constraint.
ALLOWED_DOCUMENT_TYPES = {
    "pdf",
    "txt",
    "md",
    "doc",
    "docx",
    "csv",
    "json",
}


DOCUMENT_TYPE_MAPPING = {
    ".pdf": "pdf",
    ".txt": "txt",
    ".md": "md",
    ".doc": "doc",
    ".docx": "docx",
    ".csv": "csv",
    ".json": "json",
}


# =============================================================================
# General helpers
# =============================================================================

def _utc_now() -> datetime:
    """
    Return the current UTC datetime.
    """

    return datetime.now(timezone.utc)


def _sanitize_filename(filename: str) -> str:
    """
    Remove unsafe path and special characters from a filename.
    """

    safe_filename = Path(filename).name.strip()

    if not safe_filename:
        safe_filename = "document"

    safe_filename = re.sub(
        r"[^A-Za-z0-9._-]",
        "_",
        safe_filename,
    )

    safe_filename = re.sub(
        r"_+",
        "_",
        safe_filename,
    )

    return safe_filename[:255]


def _get_extension(filename: str) -> str:
    """
    Return a lowercase extension, including the dot.
    """

    return Path(filename).suffix.lower()


def _validate_file_extension(filename: str) -> str:
    """
    Validate the extension and return it.
    """

    extension = _get_extension(filename)

    if not extension:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file does not have a file extension.",
        )

    if extension not in ALLOWED_EXTENSIONS:
        allowed_extensions = ", ".join(
            sorted(ALLOWED_EXTENSIONS)
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Unsupported file type '{extension}'. "
                f"Allowed file types: {allowed_extensions}."
            ),
        )

    return extension


def _get_document_type(
    extension: str,
    requested_document_type: Optional[str],
) -> str:
    """
    Resolve a valid document type.

    Swagger may automatically place the word 'string' inside optional
    text fields. That placeholder must not be stored in PostgreSQL.

    When the supplied value is empty or equals 'string', this function
    detects the document type from the uploaded file extension.
    """

    inferred_type = DOCUMENT_TYPE_MAPPING.get(
        extension,
        extension.lstrip("."),
    )

    if requested_document_type is None:
        return inferred_type

    cleaned_type = requested_document_type.strip().lower()

    if not cleaned_type:
        return inferred_type

    if cleaned_type in {
        "string",
        "none",
        "null",
        "undefined",
    }:
        return inferred_type

    # Accept common aliases and convert them to database values.
    aliases = {
        "text": "txt",
        "markdown": "md",
        "word": "docx",
        "msword": "doc",
        "application/pdf": "pdf",
        "text/plain": "txt",
    }

    cleaned_type = aliases.get(
        cleaned_type,
        cleaned_type,
    )

    if cleaned_type not in ALLOWED_DOCUMENT_TYPES:
        allowed_types = ", ".join(
            sorted(ALLOWED_DOCUMENT_TYPES)
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid document_type '{cleaned_type}'. "
                f"Allowed values: {allowed_types}."
            ),
        )

    return cleaned_type


def _get_document_columns() -> set[str]:
    """
    Return all actual columns declared in the Document SQLAlchemy model.
    """

    return {
        column.name
        for column in Document.__table__.columns
    }


def _filter_document_values(values: dict) -> dict:
    """
    Remove values that do not exist in the current Document model.
    """

    document_columns = _get_document_columns()

    return {
        key: value
        for key, value in values.items()
        if key in document_columns
    }


# =============================================================================
# File storage
# =============================================================================

def _save_uploaded_file(
    upload_file: UploadFile,
    stored_file_name: str,
) -> tuple[Path, int, str]:
    """
    Save the uploaded file.

    Returns:
        file path,
        file size,
        SHA-256 file hash
    """

    saved_path = UPLOAD_DIRECTORY / stored_file_name

    file_hash = hashlib.sha256()
    total_size = 0

    try:
        upload_file.file.seek(0)

        with saved_path.open("wb") as destination:
            while True:
                chunk = upload_file.file.read(
                    1024 * 1024
                )

                if not chunk:
                    break

                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=(
                            "Uploaded file exceeds the maximum allowed "
                            f"size of {MAX_FILE_SIZE_MB} MB."
                        ),
                    )

                destination.write(chunk)
                file_hash.update(chunk)

        if total_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is empty.",
            )

        return (
            saved_path,
            total_size,
            file_hash.hexdigest(),
        )

    except HTTPException:
        saved_path.unlink(
            missing_ok=True
        )
        raise

    except OSError as exc:
        saved_path.unlink(
            missing_ok=True
        )

        logger.exception(
            "Failed to save uploaded document."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save the uploaded document.",
        ) from exc

    finally:
        try:
            upload_file.file.seek(0)
        except Exception:
            pass


# =============================================================================
# Create document
# =============================================================================

def create_document(
    db: Session,
    upload_file: UploadFile,
    user_id: int,
    title: Optional[str] = None,
    department: str = "General",
    document_type: Optional[str] = None,
    description: Optional[str] = None,
) -> Document:
    """
    Save the uploaded file and create a Document database record.
    """

    original_file_name = _sanitize_filename(
        upload_file.filename or "document"
    )

    extension = _validate_file_extension(
        original_file_name
    )

    resolved_document_type = _get_document_type(
        extension=extension,
        requested_document_type=document_type,
    )

    stored_file_name = (
        f"{uuid4().hex}_{original_file_name}"
    )

    saved_file_path: Optional[Path] = None

    try:
        (
            saved_file_path,
            file_size,
            file_hash,
        ) = _save_uploaded_file(
            upload_file=upload_file,
            stored_file_name=stored_file_name,
        )

        resolved_title = (
            title.strip()
            if title and title.strip()
            else Path(original_file_name).stem
        )

        resolved_department = (
            department.strip()
            if department and department.strip()
            else "General"
        )

        resolved_description = (
            description.strip()
            if description
            and description.strip()
            and description.strip().lower() != "string"
            else None
        )

        document_values = {
            "id": uuid4(),
            "user_id": user_id,
            "title": resolved_title,
            "file_name": stored_file_name,
            "original_file_name": original_file_name,
            "document_type": resolved_document_type,
            "department": resolved_department,
            "description": resolved_description,
            "file_size": file_size,
            "file_path": str(saved_file_path),
            "file_hash": file_hash,
            "status": "uploaded",
            "version_number": 1,
            "processing_progress": 0,
            "chunk_count": 0,
            "embedding_model": None,
            "vector_dimension": None,
            "vector_collection": None,
            "is_deleted": False,
            "created_at": _utc_now(),
            "updated_at": _utc_now(),
            "deleted_at": None,
        }

        filtered_values = _filter_document_values(
            document_values
        )

        document = Document(
            **filtered_values
        )

        db.add(document)
        db.commit()
        db.refresh(document)

        logger.info(
            "Document created successfully. document_id=%s user_id=%s",
            document.id,
            user_id,
        )

        return document

    except HTTPException:
        db.rollback()

        if saved_file_path is not None:
            saved_file_path.unlink(
                missing_ok=True
            )

        raise

    except IntegrityError as exc:
        db.rollback()

        if saved_file_path is not None:
            saved_file_path.unlink(
                missing_ok=True
            )

        database_error = str(
            getattr(
                exc,
                "orig",
                exc,
            )
        )

        logger.exception(
            "Document insert constraint error: %s",
            database_error,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Unable to create document record because of a "
                f"database constraint: {database_error}"
            ),
        ) from exc

    except SQLAlchemyError as exc:
        db.rollback()

        if saved_file_path is not None:
            saved_file_path.unlink(
                missing_ok=True
            )

        logger.exception(
            "SQLAlchemy document upload error."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Unable to create document record: "
                f"{str(exc)}"
            ),
        ) from exc

    except Exception as exc:
        db.rollback()

        if saved_file_path is not None:
            saved_file_path.unlink(
                missing_ok=True
            )

        logger.exception(
            "Unexpected document upload error."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Unable to upload document: "
                f"{str(exc)}"
            ),
        ) from exc


# =============================================================================
# Get document by ID
# =============================================================================

def get_document_by_id(
    db: Session,
    document_id: UUID,
    user_id: int,
) -> Document:
    """
    Return one active document belonging to the specified user.
    """

    query = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == user_id,
    )

    if hasattr(Document, "is_deleted"):
        query = query.filter(
            Document.is_deleted.is_(False)
        )

    document = query.first()

    if document is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found.",
        )

    return document


# =============================================================================
# List documents
# =============================================================================

def list_documents(
    db: Session,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
    search: Optional[str] = None,
    department: Optional[str] = None,
    document_status: Optional[str] = None,
) -> tuple[list[Document], int]:
    """
    Return the user's documents and the total count.
    """

    if page < 1:
        page = 1

    if page_size < 1:
        page_size = 20

    if page_size > 100:
        page_size = 100

    query = db.query(Document).filter(
        Document.user_id == user_id
    )

    if hasattr(Document, "is_deleted"):
        query = query.filter(
            Document.is_deleted.is_(False)
        )

    if search and search.strip():
        search_value = f"%{search.strip()}%"

        query = query.filter(
            or_(
                Document.title.ilike(search_value),
                Document.file_name.ilike(search_value),
                Document.original_file_name.ilike(search_value),
            )
        )

    if department and department.strip():
        query = query.filter(
            Document.department.ilike(
                department.strip()
            )
        )

    if document_status and document_status.strip():
        query = query.filter(
            Document.status.ilike(
                document_status.strip()
            )
        )

    total = query.count()

    query = query.order_by(
        Document.created_at.desc()
    )

    offset = (
        page - 1
    ) * page_size

    documents = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return documents, total


# =============================================================================
# Soft delete document
# =============================================================================

def soft_delete_document(
    db: Session,
    document_id: UUID,
    user_id: int,
) -> Document:
    """
    Soft-delete a document.

    The database row and physical file remain available for auditing.
    """

    document = get_document_by_id(
        db=db,
        document_id=document_id,
        user_id=user_id,
    )

    try:
        document.is_deleted = True
        document.deleted_at = _utc_now()
        document.updated_at = _utc_now()

        db.add(document)
        db.commit()
        db.refresh(document)

        logger.info(
            "Document soft deleted. document_id=%s user_id=%s",
            document.id,
            user_id,
        )

        return document

    except SQLAlchemyError as exc:
        db.rollback()

        logger.exception(
            "Failed to soft delete document."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete the document.",
        ) from exc


# =============================================================================
# Optional physical file removal
# =============================================================================

def remove_document_file(
    document: Document,
) -> bool:
    """
    Permanently remove a document's physical file.

    This function is not called during soft deletion.
    """

    file_path = getattr(
        document,
        "file_path",
        None,
    )

    if not file_path:
        return False

    path = Path(file_path)

    if not path.exists():
        return False

    try:
        path.unlink()
        return True

    except OSError:
        logger.exception(
            "Unable to remove file: %s",
            path,
        )
        return False
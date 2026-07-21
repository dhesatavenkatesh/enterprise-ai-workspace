from __future__ import annotations

import math
from typing import Any
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.api.dependencies.rbac import (
    require_admin,
    require_admin_or_manager,
)
from app.database.session import get_db
from app.models.user import User
from app.rag.document_upload import (
    create_document,
    get_document_by_id,
    list_documents,
    soft_delete_document,
)
from app.rag.rag_service import (
    DocumentIndexingError,
    DocumentNotFoundError,
    RAGService,
)
from app.schemas.document import (
    DocumentDeleteResponse,
    DocumentListResponse,
    DocumentResponse,
    DocumentStatusResponse,
    DocumentUploadResponse,
)


router = APIRouter(
    prefix="/api/documents",
    tags=["Enterprise Knowledge Documents"],
)


# ============================================================
# Document upload
# Admin and Manager only
# ============================================================


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a knowledge-base document",
)
def upload_document(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    document_type: str | None = Form(default=None),
    department: str = Form(default="General"),
    description: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
) -> DocumentUploadResponse:
    """
    Upload a PDF, DOCX, TXT or Markdown document.

    Only users with the admin or manager role can upload
    enterprise knowledge-base documents.
    """

    try:
        document = create_document(
            db=db,
            upload_file=file,
            user_id=current_user.id,
            title=title,
            department=department,
            document_type=document_type,
            description=description,
        )

        return DocumentUploadResponse(
            message="Document uploaded successfully.",
            document=DocumentResponse.model_validate(document),
        )

    except HTTPException:
        raise

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document upload failed: {exc}",
        ) from exc


# ============================================================
# Document listing
# All authenticated users
# ============================================================


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="List uploaded documents",
)
def get_documents(
    page: int = Query(
        default=1,
        ge=1,
        description="Page number",
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
        description="Number of documents per page",
    ),
    search: str | None = Query(
        default=None,
        description="Search by title or filename",
    ),
    department: str | None = Query(
        default=None,
        description="Filter by department",
    ),
    document_status: str | None = Query(
        default=None,
        alias="status",
        description="Filter by processing status",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentListResponse:
    """
    Return documents belonging to the authenticated user.

    At this stage, each user can see only documents associated
    with their own user ID.
    """

    try:
        documents, total = list_documents(
            db=db,
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            search=search,
            department=department,
            document_status=document_status,
        )

        total_pages = (
            math.ceil(total / page_size)
            if total > 0
            else 0
        )

        return DocumentListResponse(
            items=[
                DocumentResponse.model_validate(document)
                for document in documents
            ],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    except HTTPException:
        raise

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to retrieve documents: {exc}",
        ) from exc


# ============================================================
# Document indexing
# Admin and Manager only
# ============================================================


@router.post(
    "/{document_id}/index",
    status_code=status.HTTP_200_OK,
    summary="Index a document into the knowledge base",
)
def index_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
) -> dict[str, Any]:
    """
    Process an uploaded document, create chunks and embeddings,
    and store the vectors in ChromaDB.

    Only admins and managers can index documents.

    Existing vectors for the selected document are replaced.
    """

    try:
        # Confirm that the document exists and belongs to the user.
        get_document_by_id(
            db=db,
            document_id=document_id,
            user_id=current_user.id,
        )

        rag_service = RAGService(db=db)

        result = rag_service.index_document(
            document_id=document_id,
            chunk_size=512,
            chunk_overlap=50,
            replace_existing=True,
        )

        return {
            "message": "Document indexed successfully.",
            "data": result.to_dict(),
        }

    except DocumentNotFoundError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DocumentIndexingError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    except HTTPException:
        db.rollback()
        raise

    except ValueError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected indexing error: {exc}",
        ) from exc


# ============================================================
# Document status
# All authenticated users
# ============================================================


@router.get(
    "/{document_id}/status",
    response_model=DocumentStatusResponse,
    summary="Get document processing status",
)
def get_document_status(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentStatusResponse:
    """
    Return the upload, processing and indexing status of a document.

    Users can check only documents associated with their account.
    """

    try:
        document = get_document_by_id(
            db=db,
            document_id=document_id,
            user_id=current_user.id,
        )

        return DocumentStatusResponse(
            id=document.id,
            status=document.status,
            processing_progress=document.processing_progress,
            chunk_count=document.chunk_count,
            embedding_model=document.embedding_model,
            vector_dimension=document.vector_dimension,
            vector_collection=document.vector_collection,
        )

    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to retrieve document status: {exc}",
        ) from exc


# ============================================================
# Document details
# All authenticated users
# ============================================================


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="Get document details",
)
def get_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentResponse:
    """
    Return one document belonging to the authenticated user.
    """

    try:
        document = get_document_by_id(
            db=db,
            document_id=document_id,
            user_id=current_user.id,
        )

        return DocumentResponse.model_validate(document)

    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to retrieve document: {exc}",
        ) from exc


# ============================================================
# Document deletion
# Admin only
# ============================================================


@router.delete(
    "/{document_id}",
    response_model=DocumentDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a document",
)
def delete_document(
    document_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> DocumentDeleteResponse:
    """
    Soft-delete a document.

    Only administrators can delete documents.

    The database record is marked as deleted instead of being
    permanently removed.
    """

    try:
        document = soft_delete_document(
            db=db,
            document_id=document_id,
            user_id=current_user.id,
        )

        return DocumentDeleteResponse(
            message="Document deleted successfully.",
            document_id=document.id,
        )

    except DocumentNotFoundError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document deletion failed: {exc}",
        ) from exc
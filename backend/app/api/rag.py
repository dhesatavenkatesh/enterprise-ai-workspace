from __future__ import annotations

import logging
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.rag.rag_service import (
    DocumentFileNotFoundError,
    DocumentIndexingError,
    DocumentNotFoundError,
    RAGSearchError,
    RAGServiceError,
    get_rag_service,
)
from app.schemas.rag import (
    DocumentIndexDeleteResponse,
    DocumentIndexRequest,
    DocumentIndexResponse,
    DocumentIndexStatusResponse,
    RAGAnalyticsResponse,
    RAGChatRequest,
    RAGChatResponse,
    RAGSearchRequest,
    RAGSearchResponse,
)


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/rag",
    tags=["Enterprise Knowledge RAG"],
)


# =============================================================================
# Temporary authentication dependency
# =============================================================================


def get_authenticated_user_id() -> int:
    """
    Temporary authentication dependency.

    Replace this function with the project's real authenticated
    user dependency when JWT authentication is connected.
    """

    return 1


# =============================================================================
# Document indexing
# =============================================================================


@router.post(
    "/documents/{document_id}/index",
    response_model=DocumentIndexResponse,
    status_code=status.HTTP_200_OK,
    summary="Index a document",
    description=(
        "Extracts text, creates chunks, generates embeddings, "
        "stores vectors in ChromaDB and saves chunk metadata "
        "in PostgreSQL."
    ),
)
def index_document(
    document_id: UUID,
    payload: DocumentIndexRequest,
    db: Session = Depends(get_db),
) -> dict:
    try:
        service = get_rag_service(db)

        result = service.index_document(
            document_id=document_id,
            chunk_size=payload.chunk_size,
            chunk_overlap=payload.chunk_overlap,
            replace_existing=payload.replace_existing,
        )

        return result.to_dict()

    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DocumentFileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DocumentIndexingError as exc:
        logger.exception(
            "Document indexing failed for document %s.",
            document_id,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unexpected document indexing error."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "An unexpected error occurred while indexing "
                "the document."
            ),
        ) from exc


@router.get(
    "/documents/{document_id}/index-status",
    response_model=DocumentIndexStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get document indexing status",
)
def document_index_status(
    document_id: UUID,
    db: Session = Depends(get_db),
) -> dict:
    try:
        service = get_rag_service(db)

        return service.get_document_index_status(
            document_id
        )

    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unable to retrieve indexing status."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Unable to retrieve document indexing status."
            ),
        ) from exc


@router.delete(
    "/documents/{document_id}/index",
    response_model=DocumentIndexDeleteResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete document index",
)
def delete_document_index(
    document_id: UUID,
    db: Session = Depends(get_db),
) -> dict:
    try:
        service = get_rag_service(db)

        return service.remove_document_index(
            document_id
        )

    except DocumentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except DocumentIndexingError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unable to remove document index."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to remove the document index.",
        ) from exc


# =============================================================================
# Semantic search
# =============================================================================


@router.post(
    "/search",
    response_model=RAGSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Search indexed enterprise documents",
)
def rag_search(
    payload: RAGSearchRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(
        get_authenticated_user_id
    ),
) -> dict:
    try:
        service = get_rag_service(db)

        result = service.search(
            query=payload.query.strip(),
            top_k=payload.top_k,
            document_id=(
                str(payload.document_id)
                if payload.document_id
                else None
            ),
            department=payload.department,
            document_type=payload.document_type,
            minimum_similarity=(
                payload.minimum_similarity
            ),
            user_id=user_id,
        )

        return result.to_dict()

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except RAGSearchError as exc:
        logger.exception(
            "Enterprise document search failed."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unexpected RAG search error."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "An unexpected error occurred during search."
            ),
        ) from exc


# =============================================================================
# RAG chat
# =============================================================================


@router.post(
    "/chat",
    response_model=RAGChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a question using enterprise documents",
)
def rag_chat(
    payload: RAGChatRequest,
    db: Session = Depends(get_db),
    user_id: int = Depends(
        get_authenticated_user_id
    ),
) -> dict:
    try:
        service = get_rag_service(db)

        result = service.answer_question(
            query=payload.query.strip(),
            top_k=payload.top_k,
            document_id=(
                str(payload.document_id)
                if payload.document_id
                else None
            ),
            department=payload.department,
            document_type=payload.document_type,
            minimum_similarity=(
                payload.minimum_similarity
            ),
            user_id=user_id,
        )

        return result.to_dict()

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    except RAGSearchError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    except RAGServiceError as exc:
        logger.exception(
            "RAG answer generation failed."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        logger.exception(
            "Unexpected RAG chat error."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "An unexpected error occurred while generating "
                "the answer."
            ),
        ) from exc


# =============================================================================
# Analytics
# =============================================================================


@router.get(
    "/analytics",
    response_model=RAGAnalyticsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get RAG analytics",
)
def rag_analytics(
    db: Session = Depends(get_db),
) -> dict:
    try:
        service = get_rag_service(db)

        return service.get_analytics()

    except Exception as exc:
        logger.exception(
            "Unable to retrieve RAG analytics."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve RAG analytics.",
        ) from exc
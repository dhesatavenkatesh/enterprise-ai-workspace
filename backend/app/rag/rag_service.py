from __future__ import annotations

import json
import logging
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.document import Document
from app.rag.document_processor import DocumentProcessingError, ProcessedDocument, process_document
from app.rag.embedding_service import EmbeddingService, get_embedding_service
from app.rag.vector_store import VectorStore, VectorStoreError, get_vector_store

logger = logging.getLogger(__name__)

DEFAULT_TOP_K = 5
DEFAULT_MINIMUM_SIMILARITY = 0.25
DEFAULT_CHUNK_SIZE = 512
DEFAULT_CHUNK_OVERLAP = 50


class RAGServiceError(Exception):
    """Base exception for RAG operations."""


class DocumentNotFoundError(RAGServiceError):
    """Raised when a requested document does not exist."""


class DocumentFileNotFoundError(RAGServiceError):
    """Raised when the uploaded document file cannot be found."""


class DocumentIndexingError(RAGServiceError):
    """Raised when document indexing fails."""


class RAGSearchError(RAGServiceError):
    """Raised when semantic search fails."""


@dataclass
class RAGCitation:
    citation_number: int
    document_id: str
    document_title: str
    file_name: str
    chunk_index: int
    content: str
    similarity: float
    department: str | None = None
    page_number: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RAGSearchResult:
    query: str
    results: list[dict[str, Any]]
    citations: list[RAGCitation]
    result_count: int
    search_time_ms: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "results": self.results,
            "citations": [citation.to_dict() for citation in self.citations],
            "result_count": self.result_count,
            "search_time_ms": self.search_time_ms,
        }


@dataclass
class RAGAnswer:
    query: str
    answer: str
    citations: list[RAGCitation]
    sources_used: int
    context: str
    search_time_ms: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "query": self.query,
            "answer": self.answer,
            "citations": [citation.to_dict() for citation in self.citations],
            "sources_used": self.sources_used,
            "context": self.context,
            "search_time_ms": self.search_time_ms,
        }


@dataclass
class DocumentIndexResult:
    document_id: str
    status: str
    chunks_created: int
    vectors_stored: int
    embedding_model: str
    embedding_dimension: int
    processed_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


LLMCallable = Callable[[str, str], str]


class RAGService:
    """Coordinates document processing, embeddings, ChromaDB and PostgreSQL."""

    def __init__(
        self,
        *,
        db: Session,
        vector_store: VectorStore | None = None,
        embedding_service: EmbeddingService | None = None,
        llm_callable: LLMCallable | None = None,
    ) -> None:
        self.db = db
        self.embedding_service = embedding_service or get_embedding_service()
        self.vector_store = vector_store or get_vector_store()
        self.llm_callable = llm_callable

    def index_document(
        self,
        document_id: str | UUID,
        *,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        replace_existing: bool = True,
    ) -> DocumentIndexResult:
        normalized_id = str(document_id)
        document = self._get_document(normalized_id)

        if document is None:
            raise DocumentNotFoundError(f"Document {normalized_id} was not found.")

        file_path = Path(str(document.file_path))
        if not file_path.is_absolute():
            file_path = Path.cwd() / file_path
        file_path = file_path.resolve()

        if not file_path.exists():
            self._safe_set_failed_status(document)
            raise DocumentFileNotFoundError(f"Document file was not found: {file_path}")

        try:
            self._update_document_status(document=document, status="processing", progress=10)

            metadata = {
                "document_id": normalized_id,
                "document_title": document.title,
                "file_name": document.file_name,
                "original_file_name": document.original_file_name or document.file_name,
                "department": document.department or "General",
                "document_type": document.document_type,
                "version_number": document.version_number or 1,
                "user_id": document.user_id,
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
            }

            processed = process_document(
                document_id=normalized_id,
                file_path=file_path,
                file_name=document.file_name,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                metadata=metadata,
            )

            self._update_document_status(document=document, status="processing", progress=40)
            embedded_chunks = self.embedding_service.embed_chunks(processed.chunks)
            self._update_document_status(document=document, status="processing", progress=65)

            if replace_existing:
                self.vector_store.delete_document(normalized_id)
                self._delete_postgres_chunks(normalized_id)

            vectors_stored = self.vector_store.add_embedded_chunks(embedded_chunks)
            self._update_document_status(document=document, status="processing", progress=85)

            try:
                self._save_postgres_chunks(
                    processed_document=processed,
                    embedded_chunks=embedded_chunks,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                )
            except Exception:
                self.vector_store.delete_document(normalized_id)
                raise

            document.status = "completed"
            document.processing_progress = 100
            document.chunk_count = len(processed.chunks)
            document.embedding_model = self.embedding_service.model_name
            document.vector_dimension = self.embedding_service.embedding_dimension
            document.vector_collection = self.vector_store.collection_name
            document.updated_at = datetime.now(UTC)
            self.db.commit()
            self.db.refresh(document)

            return DocumentIndexResult(
                document_id=normalized_id,
                status="completed",
                chunks_created=len(processed.chunks),
                vectors_stored=vectors_stored,
                embedding_model=self.embedding_service.model_name,
                embedding_dimension=self.embedding_service.embedding_dimension,
                processed_at=datetime.now(UTC).isoformat(),
            )

        except (DocumentNotFoundError, DocumentFileNotFoundError, DocumentIndexingError):
            raise
        except (DocumentProcessingError, VectorStoreError) as exc:
            self.db.rollback()
            self._safe_set_failed_status_by_id(normalized_id)
            logger.exception("Document indexing failed: document_id=%s", normalized_id)
            raise DocumentIndexingError(f"Unable to index document: {exc}") from exc
        except Exception as exc:
            self.db.rollback()
            self._safe_set_failed_status_by_id(normalized_id)
            logger.exception("Unexpected document indexing failure: %s", normalized_id)
            raise DocumentIndexingError(f"Unable to index document: {exc}") from exc

    def search(
        self,
        query: str,
        *,
        top_k: int = DEFAULT_TOP_K,
        document_id: str | None = None,
        department: str | None = None,
        document_type: str | None = None,
        minimum_similarity: float = DEFAULT_MINIMUM_SIMILARITY,
        user_id: int | None = None,
    ) -> RAGSearchResult:
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Search query cannot be empty.")
        if top_k <= 0:
            raise ValueError("top_k must be greater than zero.")
        if not 0 <= minimum_similarity <= 1:
            raise ValueError("minimum_similarity must be between 0 and 1.")

        started_at = datetime.now(UTC)
        try:
            results = self.vector_store.search(
                query=query.strip(),
                top_k=top_k,
                document_id=document_id,
                department=department,
                document_type=document_type,
                minimum_similarity=minimum_similarity,
            )
            citations = self._build_citations(results)
            elapsed_ms = (datetime.now(UTC) - started_at).total_seconds() * 1000
            self._save_search_log(
                query=query.strip(),
                user_id=user_id,
                result_count=len(results),
                search_time_ms=elapsed_ms,
                document_id=document_id,
                department=department,
                document_type=document_type,
            )
            return RAGSearchResult(
                query=query.strip(),
                results=results,
                citations=citations,
                result_count=len(results),
                search_time_ms=round(elapsed_ms, 2),
            )
        except Exception as exc:
            logger.exception("RAG search failed: query=%s", query)
            if isinstance(exc, ValueError):
                raise
            raise RAGSearchError(f"RAG search failed: {exc}") from exc

    def answer_question(
        self,
        query: str,
        *,
        top_k: int = DEFAULT_TOP_K,
        document_id: str | None = None,
        department: str | None = None,
        document_type: str | None = None,
        minimum_similarity: float = DEFAULT_MINIMUM_SIMILARITY,
        user_id: int | None = None,
    ) -> RAGAnswer:
        search_result = self.search(
            query=query,
            top_k=top_k,
            document_id=document_id,
            department=department,
            document_type=document_type,
            minimum_similarity=minimum_similarity,
            user_id=user_id,
        )

        if not search_result.citations:
            return RAGAnswer(
                query=query,
                answer="I could not find relevant information in the enterprise knowledge base.",
                citations=[],
                sources_used=0,
                context="",
                search_time_ms=search_result.search_time_ms,
            )

        context = self._build_context(search_result.citations)
        answer = (
            self._generate_llm_answer(query=query, context=context)
            if self.llm_callable is not None
            else self._generate_extractive_answer(search_result.citations)
        )

        return RAGAnswer(
            query=query,
            answer=answer,
            citations=search_result.citations,
            sources_used=len(search_result.citations),
            context=context,
            search_time_ms=search_result.search_time_ms,
        )

    def remove_document_index(self, document_id: str | UUID) -> dict[str, Any]:
        normalized_id = str(document_id)
        try:
            vectors_deleted = self.vector_store.delete_document(normalized_id)
            rows_deleted = self._delete_postgres_chunks(normalized_id)
            document = self._get_document(normalized_id)
            if document is not None:
                document.status = "uploaded"
                document.processing_progress = 0
                document.chunk_count = 0
                document.embedding_model = None
                document.vector_dimension = None
                document.vector_collection = None
                document.updated_at = datetime.now(UTC)
                self.db.commit()
            return {
                "document_id": normalized_id,
                "vectors_deleted": vectors_deleted,
                "database_chunks_deleted": rows_deleted,
                "status": "removed",
            }
        except Exception as exc:
            self.db.rollback()
            if isinstance(exc, RAGServiceError):
                raise
            raise DocumentIndexingError(f"Unable to remove document index: {exc}") from exc

    def get_document_index_status(self, document_id: str | UUID) -> dict[str, Any]:
        normalized_id = str(document_id)
        document = self._get_document(normalized_id)
        if document is None:
            raise DocumentNotFoundError(f"Document {normalized_id} was not found.")
        return {
            "document_id": normalized_id,
            "status": document.status,
            "processing_progress": document.processing_progress or 0,
            "chunk_count": document.chunk_count or 0,
            "embedding_model": document.embedding_model,
            "vector_dimension": document.vector_dimension,
            "vector_collection": document.vector_collection,
            "indexed": self.vector_store.document_exists(normalized_id),
        }

    def get_analytics(self) -> dict[str, Any]:
        document_stats = (
            self.db.execute(
                text(
                    """
                SELECT
                    COUNT(*) AS total_documents,
                    COUNT(*) FILTER (WHERE status = 'completed') AS indexed_documents,
                    COUNT(*) FILTER (WHERE status = 'processing') AS processing_documents,
                    COUNT(*) FILTER (WHERE status = 'failed') AS failed_documents,
                    COALESCE(SUM(chunk_count), 0) AS total_chunks
                FROM documents
                WHERE deleted_at IS NULL
                  AND is_deleted = FALSE
                """
                )
            )
            .mappings()
            .one()
        )

        return {
            "documents": {
                "total": int(document_stats["total_documents"] or 0),
                "indexed": int(document_stats["indexed_documents"] or 0),
                "processing": int(document_stats["processing_documents"] or 0),
                "failed": int(document_stats["failed_documents"] or 0),
                "chunks": int(document_stats["total_chunks"] or 0),
            },
            "searches": self._get_search_stats(),
            "vector_store": self.vector_store.collection_information(),
        }

    def _get_document(self, document_id: str) -> Document | None:
        try:
            normalized_uuid = UUID(document_id)
        except ValueError as exc:
            raise ValueError("Invalid document UUID.") from exc

        return (
            self.db.query(Document)
            .filter(
                Document.id == normalized_uuid,
                Document.deleted_at.is_(None),
                Document.is_deleted.is_(False),
            )
            .first()
        )

    def _update_document_status(self, *, document: Document, status: str, progress: int) -> None:
        document.status = status
        document.processing_progress = max(0, min(100, int(progress)))
        document.updated_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(document)

    def _safe_set_failed_status(self, document: Document) -> None:
        try:
            self._update_document_status(document=document, status="failed", progress=0)
        except Exception:
            self.db.rollback()
            logger.exception("Unable to set document status to failed.")

    def _safe_set_failed_status_by_id(self, document_id: str) -> None:
        try:
            document = self._get_document(document_id)
            if document is not None:
                self._safe_set_failed_status(document)
        except Exception:
            self.db.rollback()
            logger.exception("Unable to update failed document status.")

    def _save_postgres_chunks(
        self,
        *,
        processed_document: ProcessedDocument,
        embedded_chunks: list[dict[str, Any]],
        chunk_size: int,
        chunk_overlap: int,
    ) -> None:
        if len(processed_document.chunks) != len(embedded_chunks):
            raise DocumentIndexingError(
                "Processed chunk count does not match embedded chunk count."
            )

        try:
            for chunk, embedded in zip(
                processed_document.chunks,
                embedded_chunks,
                strict=True,
            ):
                metadata = dict(embedded.get("metadata") or {})
                vector_id = str(embedded.get("id") or "").strip()
                if not vector_id:
                    raise DocumentIndexingError(f"Missing vector ID for chunk {chunk.chunk_index}.")

                page_number = self._optional_int(metadata.get("page_number"))
                processing_time_ms = self._optional_float(metadata.get("processing_time_ms"))
                section = metadata.get("section")
                if section is not None:
                    section = str(section)

                token_count = self._optional_int(getattr(chunk, "word_count", None))
                if token_count is None:
                    token_count = len(str(chunk.content).split())

                self.db.execute(
                    text(
                        """
                        INSERT INTO document_chunks (
                            document_id,
                            chunk_number,
                            chunk_text,
                            page_number,
                            section,
                            chunk_size,
                            chunk_overlap,
                            embedding_model,
                            vector_dimension,
                            vector_id,
                            token_count,
                            processing_time_ms,
                            metadata,
                            is_deleted
                        )
                        VALUES (
                            CAST(:document_id AS UUID),
                            :chunk_number,
                            :chunk_text,
                            :page_number,
                            :section,
                            :chunk_size,
                            :chunk_overlap,
                            :embedding_model,
                            :vector_dimension,
                            :vector_id,
                            :token_count,
                            :processing_time_ms,
                            CAST(:metadata AS JSONB),
                            FALSE
                        )
                        """
                    ),
                    {
                        "document_id": processed_document.document_id,
                        "chunk_number": int(chunk.chunk_index),
                        "chunk_text": str(chunk.content),
                        "page_number": page_number,
                        "section": section,
                        "chunk_size": int(metadata.get("chunk_size", chunk_size)),
                        "chunk_overlap": int(metadata.get("chunk_overlap", chunk_overlap)),
                        "embedding_model": self.embedding_service.model_name,
                        "vector_dimension": self.embedding_service.embedding_dimension,
                        "vector_id": vector_id,
                        "token_count": token_count,
                        "processing_time_ms": processing_time_ms,
                        "metadata": self._json_string(metadata),
                    },
                )

            self.db.commit()
            logger.info(
                "Saved %s PostgreSQL chunks for document %s.",
                len(embedded_chunks),
                processed_document.document_id,
            )
        except Exception as exc:
            self.db.rollback()
            logger.exception("Unable to save document chunks in PostgreSQL.")
            if isinstance(exc, DocumentIndexingError):
                raise
            raise DocumentIndexingError(f"Unable to save document chunks: {exc}") from exc

    def _delete_postgres_chunks(self, document_id: str) -> int:
        try:
            normalized_uuid = UUID(document_id)
        except ValueError as exc:
            raise ValueError("Invalid document UUID.") from exc

        try:
            result = self.db.execute(
                text(
                    """
                    DELETE FROM document_chunks
                    WHERE document_id = CAST(:document_id AS UUID)
                    """
                ),
                {"document_id": str(normalized_uuid)},
            )
            self.db.commit()
            return int(result.rowcount or 0)
        except Exception as exc:
            self.db.rollback()
            logger.exception("Unable to delete PostgreSQL chunks.")
            raise DocumentIndexingError(f"Unable to delete document chunks: {exc}") from exc

    def _save_search_log(
        self,
        *,
        query: str,
        user_id: int | None,
        result_count: int,
        search_time_ms: float,
        document_id: str | None,
        department: str | None,
        document_type: str | None,
    ) -> None:
        try:
            self.db.execute(
                text(
                    """
                    INSERT INTO rag_search_logs (
                        user_id,
                        query,
                        result_count,
                        search_time_ms,
                        filters,
                        created_at
                    )
                    VALUES (
                        :user_id,
                        :query,
                        :result_count,
                        :search_time_ms,
                        CAST(:filters AS JSONB),
                        NOW()
                    )
                    """
                ),
                {
                    "user_id": user_id,
                    "query": query,
                    "result_count": result_count,
                    "search_time_ms": search_time_ms,
                    "filters": self._json_string(
                        {
                            "document_id": document_id,
                            "department": department,
                            "document_type": document_type,
                        }
                    ),
                },
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            logger.warning(
                "RAG search log was not saved. The rag_search_logs table may not exist.",
                exc_info=True,
            )

    def _get_search_stats(self) -> dict[str, Any]:
        try:
            row = (
                self.db.execute(
                    text(
                        """
                    SELECT
                        COUNT(*) AS total_searches,
                        COALESCE(AVG(search_time_ms), 0) AS average_search_time_ms,
                        COALESCE(AVG(result_count), 0) AS average_result_count
                    FROM rag_search_logs
                    """
                    )
                )
                .mappings()
                .one()
            )
            return {
                "total": int(row["total_searches"] or 0),
                "average_search_time_ms": round(float(row["average_search_time_ms"] or 0), 2),
                "average_result_count": round(float(row["average_result_count"] or 0), 2),
            }
        except Exception:
            self.db.rollback()
            return {
                "total": 0,
                "average_search_time_ms": 0.0,
                "average_result_count": 0.0,
            }

    @staticmethod
    def _build_citations(results: list[dict[str, Any]]) -> list[RAGCitation]:
        citations: list[RAGCitation] = []
        for index, result in enumerate(results, start=1):
            metadata = result.get("metadata", {}) or {}
            page_number = RAGService._optional_int(metadata.get("page_number"))
            chunk_index = RAGService._optional_int(metadata.get("chunk_index"))
            citations.append(
                RAGCitation(
                    citation_number=index,
                    document_id=str(metadata.get("document_id", "")),
                    document_title=str(
                        metadata.get(
                            "document_title",
                            metadata.get("file_name", "Untitled document"),
                        )
                    ),
                    file_name=str(metadata.get("file_name", "Unknown file")),
                    chunk_index=chunk_index or 0,
                    content=str(result.get("content", "")),
                    similarity=float(result.get("similarity", 0)),
                    department=(
                        str(metadata["department"])
                        if metadata.get("department") is not None
                        else None
                    ),
                    page_number=page_number,
                )
            )
        return citations

    @staticmethod
    def _build_context(citations: list[RAGCitation]) -> str:
        context_parts: list[str] = []
        for citation in citations:
            lines = [
                f"[Source {citation.citation_number}]",
                f"Document: {citation.document_title}",
                f"File: {citation.file_name}",
                f"Chunk: {citation.chunk_index}",
            ]
            if citation.page_number is not None:
                lines.append(f"Page: {citation.page_number}")
            lines.append(f"Content: {citation.content}")
            context_parts.append("\n".join(lines))
        return "\n\n".join(context_parts)

    def _generate_llm_answer(self, *, query: str, context: str) -> str:
        if self.llm_callable is None:
            raise RAGServiceError("No LLM callable is configured.")

        system_prompt = (
            "You are an enterprise knowledge assistant. "
            "Answer only from the supplied context. "
            "Do not invent information. "
            "Use citation markers such as [Source 1]. "
            "When the answer is unavailable, say that the knowledge base "
            "does not contain enough information."
        )
        user_prompt = f"Question:\n{query}\n\nKnowledge-base context:\n{context}"

        try:
            answer = self.llm_callable(system_prompt, user_prompt)
            if not isinstance(answer, str):
                raise RAGServiceError("The LLM returned an invalid response.")
            answer = answer.strip()
            if not answer:
                raise RAGServiceError("The LLM returned an empty response.")
            return answer
        except Exception as exc:
            logger.exception("LLM answer generation failed.")
            if isinstance(exc, RAGServiceError):
                raise
            raise RAGServiceError(f"LLM answer generation failed: {exc}") from exc

    @staticmethod
    def _generate_extractive_answer(citations: list[RAGCitation]) -> str:
        answer_parts: list[str] = []
        for citation in citations[:3]:
            content = citation.content.strip()
            if content:
                answer_parts.append(f"{content} [Source {citation.citation_number}]")
        if not answer_parts:
            return "I could not find enough information in the enterprise knowledge base."
        return "\n\n".join(answer_parts)

    @staticmethod
    def _json_string(value: dict[str, Any]) -> str:
        return json.dumps(value, default=str)

    @staticmethod
    def _optional_int(value: Any) -> int | None:
        if value is None or value == "":
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _optional_float(value: Any) -> float | None:
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None


def get_rag_service(
    db: Session,
    *,
    llm_callable: LLMCallable | None = None,
) -> RAGService:
    return RAGService(db=db, llm_callable=llm_callable)

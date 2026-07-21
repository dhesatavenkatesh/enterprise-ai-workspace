from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, Sequence

import chromadb
from chromadb.api.models.Collection import Collection

from app.rag.embedding_service import (
    EmbeddingService,
    get_embedding_service,
)


logger = logging.getLogger(__name__)


DEFAULT_COLLECTION_NAME = "enterprise_knowledge_base"
DEFAULT_PERSIST_DIRECTORY = "storage/chroma_db"


class VectorStoreError(Exception):
    """Base exception for vector store operations."""


class EmptyVectorStoreInputError(VectorStoreError):
    """Raised when empty vector data is supplied."""


class VectorDimensionMismatchError(VectorStoreError):
    """Raised when an embedding has an invalid dimension."""


class VectorStore:
    """
    Persistent ChromaDB vector store for enterprise documents.

    Responsibilities:
    - create or load a collection
    - store embedded document chunks
    - run similarity searches
    - filter results by metadata
    - delete document vectors
    - provide collection statistics
    """

    def __init__(
        self,
        *,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        persist_directory: str | Path = DEFAULT_PERSIST_DIRECTORY,
        embedding_service: EmbeddingService | None = None,
    ) -> None:
        if not collection_name.strip():
            raise ValueError(
                "collection_name cannot be empty."
            )

        self.collection_name = collection_name.strip()

        self.persist_directory = Path(
            persist_directory
        ).resolve()

        self.persist_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.embedding_service = (
            embedding_service or get_embedding_service()
        )

        try:
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory),
            )

            self.collection = (
                self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={
                        "description": (
                            "Enterprise AI Workspace "
                            "knowledge-base vectors"
                        ),
                        "embedding_model": (
                            self.embedding_service.model_name
                        ),
                        "embedding_dimension": (
                            self.embedding_service.embedding_dimension
                        ),
                        "hnsw:space": "cosine",
                    },
                )
            )

            logger.info(
                "ChromaDB collection ready: "
                "collection=%s directory=%s",
                self.collection_name,
                self.persist_directory,
            )

        except Exception as exc:
            logger.exception(
                "Unable to initialize ChromaDB."
            )

            raise VectorStoreError(
                f"Unable to initialize ChromaDB: {exc}"
            ) from exc

    def add_embedded_chunks(
        self,
        embedded_chunks: Sequence[dict[str, Any]],
    ) -> int:
        """
        Adds or updates already embedded document chunks.

        Expected format:

        {
            "id": "document-id:0",
            "document": "chunk content",
            "embedding": [0.1, 0.2, ...],
            "metadata": {...}
        }
        """

        validated_chunks = self._validate_embedded_chunks(
            embedded_chunks
        )

        ids = [
            chunk["id"]
            for chunk in validated_chunks
        ]

        documents = [
            chunk["document"]
            for chunk in validated_chunks
        ]

        embeddings = [
            chunk["embedding"]
            for chunk in validated_chunks
        ]

        metadatas = [
            chunk["metadata"]
            for chunk in validated_chunks
        ]

        try:
            self.collection.upsert(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
            )

            logger.info(
                "Stored %s embedded chunks in collection %s.",
                len(ids),
                self.collection_name,
            )

            return len(ids)

        except Exception as exc:
            logger.exception(
                "Unable to store document chunks."
            )

            raise VectorStoreError(
                f"Unable to store document chunks: {exc}"
            ) from exc

    def add_document_chunks(
        self,
        chunks: Sequence[Any],
    ) -> int:
        """
        Embeds DocumentChunk objects and stores them.

        This is a shortcut for:

        embedding_service.embed_chunks(...)
        vector_store.add_embedded_chunks(...)
        """

        if not chunks:
            raise EmptyVectorStoreInputError(
                "At least one document chunk is required."
            )

        try:
            embedded_chunks = (
                self.embedding_service.embed_chunks(chunks)
            )

            return self.add_embedded_chunks(
                embedded_chunks
            )

        except VectorStoreError:
            raise
        except Exception as exc:
            logger.exception(
                "Unable to embed and store chunks."
            )

            raise VectorStoreError(
                f"Unable to embed and store chunks: {exc}"
            ) from exc

    def search(
        self,
        query: str,
        *,
        top_k: int = 5,
        document_id: str | None = None,
        department: str | None = None,
        document_type: str | None = None,
        minimum_similarity: float | None = None,
    ) -> list[dict[str, Any]]:
        """
        Searches the collection using semantic similarity.

        Optional filters:
        - document_id
        - department
        - document_type
        - minimum_similarity
        """

        if not isinstance(query, str) or not query.strip():
            raise ValueError(
                "Search query cannot be empty."
            )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        if minimum_similarity is not None:
            if not 0 <= minimum_similarity <= 1:
                raise ValueError(
                    "minimum_similarity must be "
                    "between 0 and 1."
                )

        where_filter = self._build_where_filter(
            document_id=document_id,
            department=department,
            document_type=document_type,
        )

        query_embedding = (
            self.embedding_service.embed_query(query)
        )

        query_arguments: dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
            "include": [
                "documents",
                "metadatas",
                "distances",
            ],
        }

        if where_filter:
            query_arguments["where"] = where_filter

        try:
            result = self.collection.query(
                **query_arguments
            )
        except Exception as exc:
            logger.exception(
                "Vector similarity search failed."
            )

            raise VectorStoreError(
                f"Vector similarity search failed: {exc}"
            ) from exc

        return self._format_query_results(
            result,
            minimum_similarity=minimum_similarity,
        )

    def search_by_embedding(
        self,
        embedding: Sequence[float],
        *,
        top_k: int = 5,
        where: dict[str, Any] | None = None,
        minimum_similarity: float | None = None,
    ) -> list[dict[str, Any]]:
        """
        Searches using an embedding supplied by the caller.
        """

        validated_embedding = (
            self._validate_embedding(embedding)
        )

        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        query_arguments: dict[str, Any] = {
            "query_embeddings": [
                validated_embedding
            ],
            "n_results": top_k,
            "include": [
                "documents",
                "metadatas",
                "distances",
            ],
        }

        if where:
            query_arguments["where"] = where

        try:
            result = self.collection.query(
                **query_arguments
            )

            return self._format_query_results(
                result,
                minimum_similarity=minimum_similarity,
            )

        except Exception as exc:
            logger.exception(
                "Embedding search failed."
            )

            raise VectorStoreError(
                f"Embedding search failed: {exc}"
            ) from exc

    def get_document_chunks(
        self,
        document_id: str,
        *,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Retrieves all stored chunks for one document.
        """

        if not document_id.strip():
            raise ValueError(
                "document_id cannot be empty."
            )

        arguments: dict[str, Any] = {
            "where": {
                "document_id": str(document_id),
            },
            "include": [
                "documents",
                "metadatas",
                "embeddings",
            ],
        }

        if limit is not None:
            if limit <= 0:
                raise ValueError(
                    "limit must be greater than zero."
                )

            arguments["limit"] = limit

        try:
            result = self.collection.get(
                **arguments
            )

            ids = result.get("ids", [])
            documents = result.get(
                "documents",
                [],
            )
            metadatas = result.get(
                "metadatas",
                [],
            )
            embeddings = result.get(
                "embeddings",
                [],
            )

            chunks: list[dict[str, Any]] = []

            for index, chunk_id in enumerate(ids):
                metadata = (
                    metadatas[index]
                    if index < len(metadatas)
                    else {}
                )

                chunks.append(
                    {
                        "id": chunk_id,
                        "document": (
                            documents[index]
                            if index < len(documents)
                            else ""
                        ),
                        "metadata": metadata or {},
                        "embedding": (
                            embeddings[index]
                            if index < len(embeddings)
                            else None
                        ),
                    }
                )

            chunks.sort(
                key=lambda item: int(
                    item["metadata"].get(
                        "chunk_index",
                        0,
                    )
                )
            )

            return chunks

        except Exception as exc:
            logger.exception(
                "Unable to retrieve document vectors."
            )

            raise VectorStoreError(
                f"Unable to retrieve document vectors: {exc}"
            ) from exc

    def delete_document(
        self,
        document_id: str,
    ) -> int:
        """
        Deletes all vectors belonging to one document.
        """

        if not document_id.strip():
            raise ValueError(
                "document_id cannot be empty."
            )

        try:
            existing = self.collection.get(
                where={
                    "document_id": str(document_id),
                },
                include=[],
            )

            ids = existing.get("ids", [])
            deleted_count = len(ids)

            if deleted_count == 0:
                return 0

            self.collection.delete(
                where={
                    "document_id": str(document_id),
                }
            )

            logger.info(
                "Deleted %s vectors for document %s.",
                deleted_count,
                document_id,
            )

            return deleted_count

        except Exception as exc:
            logger.exception(
                "Unable to delete document vectors."
            )

            raise VectorStoreError(
                f"Unable to delete document vectors: {exc}"
            ) from exc

    def delete_chunks(
        self,
        chunk_ids: Sequence[str],
    ) -> int:
        """
        Deletes specific vector IDs.
        """

        validated_ids = [
            chunk_id.strip()
            for chunk_id in chunk_ids
            if isinstance(chunk_id, str)
            and chunk_id.strip()
        ]

        if not validated_ids:
            raise EmptyVectorStoreInputError(
                "At least one chunk ID is required."
            )

        try:
            self.collection.delete(
                ids=validated_ids,
            )

            return len(validated_ids)

        except Exception as exc:
            logger.exception(
                "Unable to delete vector chunks."
            )

            raise VectorStoreError(
                f"Unable to delete vector chunks: {exc}"
            ) from exc

    def document_exists(
        self,
        document_id: str,
    ) -> bool:
        """
        Checks whether vectors exist for a document.
        """

        if not document_id.strip():
            return False

        try:
            result = self.collection.get(
                where={
                    "document_id": str(document_id),
                },
                limit=1,
                include=[],
            )

            return bool(result.get("ids"))

        except Exception as exc:
            raise VectorStoreError(
                f"Unable to check document vectors: {exc}"
            ) from exc

    def count(self) -> int:
        """
        Returns the total number of stored chunks.
        """

        try:
            return int(self.collection.count())
        except Exception as exc:
            raise VectorStoreError(
                f"Unable to count vectors: {exc}"
            ) from exc

    def collection_information(
        self,
    ) -> dict[str, Any]:
        """
        Returns collection status information.
        """

        return {
            "collection_name": self.collection_name,
            "persist_directory": str(
                self.persist_directory
            ),
            "vector_count": self.count(),
            "embedding_model": (
                self.embedding_service.model_name
            ),
            "embedding_dimension": (
                self.embedding_service.embedding_dimension
            ),
            "metadata": self.collection.metadata,
        }

    def reset_collection(self) -> Collection:
        """
        Deletes and recreates the complete collection.

        Use carefully because all stored vectors are removed.
        """

        try:
            self.client.delete_collection(
                name=self.collection_name
            )

            self.collection = (
                self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={
                        "description": (
                            "Enterprise AI Workspace "
                            "knowledge-base vectors"
                        ),
                        "embedding_model": (
                            self.embedding_service.model_name
                        ),
                        "embedding_dimension": (
                            self.embedding_service.embedding_dimension
                        ),
                        "hnsw:space": "cosine",
                    },
                )
            )

            logger.warning(
                "Vector collection reset: %s",
                self.collection_name,
            )

            return self.collection

        except Exception as exc:
            logger.exception(
                "Unable to reset vector collection."
            )

            raise VectorStoreError(
                f"Unable to reset vector collection: {exc}"
            ) from exc

    def _validate_embedded_chunks(
        self,
        embedded_chunks: Sequence[
            dict[str, Any]
        ],
    ) -> list[dict[str, Any]]:
        if not embedded_chunks:
            raise EmptyVectorStoreInputError(
                "At least one embedded chunk is required."
            )

        validated: list[dict[str, Any]] = []

        for position, chunk in enumerate(
            embedded_chunks
        ):
            if not isinstance(chunk, dict):
                raise TypeError(
                    f"Chunk at position {position} "
                    "must be a dictionary."
                )

            chunk_id = chunk.get("id")
            document = chunk.get("document")
            embedding = chunk.get("embedding")
            metadata = chunk.get("metadata", {})

            if not isinstance(
                chunk_id,
                str,
            ) or not chunk_id.strip():
                raise VectorStoreError(
                    f"Chunk at position {position} "
                    "has an invalid ID."
                )

            if not isinstance(
                document,
                str,
            ) or not document.strip():
                raise VectorStoreError(
                    f"Chunk at position {position} "
                    "has empty document content."
                )

            if not isinstance(metadata, dict):
                raise VectorStoreError(
                    f"Chunk at position {position} "
                    "has invalid metadata."
                )

            validated_embedding = (
                self._validate_embedding(
                    embedding
                )
            )

            validated.append(
                {
                    "id": chunk_id.strip(),
                    "document": document.strip(),
                    "embedding": (
                        validated_embedding
                    ),
                    "metadata": (
                        self._prepare_metadata(
                            metadata
                        )
                    ),
                }
            )

        return validated

    def _validate_embedding(
        self,
        embedding: Sequence[float] | None,
    ) -> list[float]:
        if embedding is None:
            raise VectorStoreError(
                "Embedding cannot be missing."
            )

        if isinstance(embedding, str):
            raise TypeError(
                "Embedding must be a numeric sequence."
            )

        try:
            vector = [
                float(value)
                for value in embedding
            ]
        except (TypeError, ValueError) as exc:
            raise VectorStoreError(
                "Embedding contains invalid values."
            ) from exc

        expected_dimension = (
            self.embedding_service.embedding_dimension
        )

        if len(vector) != expected_dimension:
            raise VectorDimensionMismatchError(
                "Embedding dimension mismatch. "
                f"Expected {expected_dimension}, "
                f"received {len(vector)}."
            )

        return vector

    @staticmethod
    def _prepare_metadata(
        metadata: dict[str, Any],
    ) -> dict[str, str | int | float | bool]:
        prepared: dict[
            str,
            str | int | float | bool
        ] = {}

        for key, value in metadata.items():
            if value is None:
                continue

            field_name = str(key)

            if isinstance(
                value,
                (str, int, float, bool),
            ):
                prepared[field_name] = value
            else:
                prepared[field_name] = str(
                    value
                )

        return prepared

    @staticmethod
    def _build_where_filter(
        *,
        document_id: str | None,
        department: str | None,
        document_type: str | None,
    ) -> dict[str, Any] | None:
        conditions: list[dict[str, Any]] = []

        if document_id:
            conditions.append(
                {
                    "document_id": str(
                        document_id
                    )
                }
            )

        if department:
            conditions.append(
                {
                    "department": (
                        department.strip()
                    )
                }
            )

        if document_type:
            conditions.append(
                {
                    "document_type": (
                        document_type.strip()
                    )
                }
            )

        if not conditions:
            return None

        if len(conditions) == 1:
            return conditions[0]

        return {
            "$and": conditions,
        }

    @staticmethod
    def _format_query_results(
        result: dict[str, Any],
        *,
        minimum_similarity: float | None,
    ) -> list[dict[str, Any]]:
        ids = result.get("ids") or [[]]
        documents = result.get(
            "documents"
        ) or [[]]
        metadatas = result.get(
            "metadatas"
        ) or [[]]
        distances = result.get(
            "distances"
        ) or [[]]

        result_ids = ids[0] if ids else []
        result_documents = (
            documents[0]
            if documents
            else []
        )
        result_metadatas = (
            metadatas[0]
            if metadatas
            else []
        )
        result_distances = (
            distances[0]
            if distances
            else []
        )

        formatted: list[dict[str, Any]] = []

        for index, chunk_id in enumerate(
            result_ids
        ):
            distance = (
                float(result_distances[index])
                if index < len(
                    result_distances
                )
                else 1.0
            )

            similarity = max(
                0.0,
                min(1.0, 1.0 - distance),
            )

            if (
                minimum_similarity is not None
                and similarity
                < minimum_similarity
            ):
                continue

            formatted.append(
                {
                    "id": chunk_id,
                    "content": (
                        result_documents[index]
                        if index
                        < len(result_documents)
                        else ""
                    ),
                    "metadata": (
                        result_metadatas[index]
                        if index
                        < len(result_metadatas)
                        else {}
                    )
                    or {},
                    "distance": distance,
                    "similarity": similarity,
                    "rank": index + 1,
                }
            )

        return formatted


@lru_cache(maxsize=4)
def get_vector_store(
    collection_name: str = (
        DEFAULT_COLLECTION_NAME
    ),
    persist_directory: str = (
        DEFAULT_PERSIST_DIRECTORY
    ),
) -> VectorStore:
    """
    Returns a cached VectorStore instance.
    """

    return VectorStore(
        collection_name=collection_name,
        persist_directory=persist_directory,
    )
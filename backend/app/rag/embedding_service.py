from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any, Iterable, Sequence

import numpy as np
from sentence_transformers import SentenceTransformer


logger = logging.getLogger(__name__)


# =============================================================================
# Configuration
# =============================================================================

DEFAULT_EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL_NAME",
    "sentence-transformers/all-MiniLM-L6-v2",
)

DEFAULT_BATCH_SIZE = int(
    os.getenv(
        "EMBEDDING_BATCH_SIZE",
        "32",
    )
)

DEFAULT_EMBEDDING_DIMENSION = int(
    os.getenv(
        "EMBEDDING_DIMENSION",
        "384",
    )
)

DEFAULT_NORMALIZE_EMBEDDINGS = (
    os.getenv(
        "NORMALIZE_EMBEDDINGS",
        "true",
    )
    .strip()
    .lower()
    in {
        "true",
        "1",
        "yes",
        "on",
    }
)


# =============================================================================
# Exceptions
# =============================================================================

class EmbeddingServiceError(Exception):
    """
    Base exception for embedding service operations.
    """


class EmptyEmbeddingInputError(EmbeddingServiceError):
    """
    Raised when empty text is provided.
    """


class InvalidEmbeddingError(EmbeddingServiceError):
    """
    Raised when an invalid embedding vector is generated.
    """


# =============================================================================
# Validation helpers
# =============================================================================

def _clean_text(text: str) -> str:
    """
    Validate and clean one text value.
    """

    if not isinstance(text, str):
        raise InvalidEmbeddingError(
            "Embedding input must be a string."
        )

    cleaned_text = text.strip()

    if not cleaned_text:
        raise EmptyEmbeddingInputError(
            "Cannot generate an embedding for empty text."
        )

    return cleaned_text


def _clean_texts(
    texts: Iterable[str],
) -> list[str]:
    """
    Validate and clean multiple text values.
    """

    if texts is None:
        raise EmptyEmbeddingInputError(
            "Embedding input cannot be None."
        )

    cleaned_texts = [
        _clean_text(text)
        for text in texts
    ]

    if not cleaned_texts:
        raise EmptyEmbeddingInputError(
            "At least one text value is required."
        )

    return cleaned_texts


def _embedding_to_list(
    embedding: np.ndarray | Sequence[float],
) -> list[float]:
    """
    Convert NumPy embeddings into a normal list of floats.
    """

    if isinstance(embedding, np.ndarray):
        return (
            embedding
            .astype(np.float32)
            .tolist()
        )

    return [
        float(value)
        for value in embedding
    ]


def validate_embedding(
    embedding: Sequence[float],
    expected_dimension: int | None = None,
) -> int:
    """
    Validate an embedding vector.

    Returns the vector dimension.
    """

    if embedding is None:
        raise InvalidEmbeddingError(
            "Embedding cannot be None."
        )

    if isinstance(embedding, str):
        raise InvalidEmbeddingError(
            "Embedding must be a numeric sequence."
        )

    vector_dimension = len(embedding)

    if vector_dimension == 0:
        raise InvalidEmbeddingError(
            "Embedding vector cannot be empty."
        )

    if (
        expected_dimension is not None
        and vector_dimension != expected_dimension
    ):
        raise InvalidEmbeddingError(
            "Embedding dimension mismatch. "
            f"Expected {expected_dimension}, "
            f"received {vector_dimension}."
        )

    for value in embedding:
        if not isinstance(
            value,
            (
                int,
                float,
                np.integer,
                np.floating,
            ),
        ):
            raise InvalidEmbeddingError(
                "Embedding contains a non-numeric value."
            )

        if not np.isfinite(float(value)):
            raise InvalidEmbeddingError(
                "Embedding contains NaN or infinite values."
            )

    return vector_dimension


def validate_embedding_dimension(
    embedding: Sequence[float],
    expected_dimension: int | None = None,
) -> int:
    """
    Compatibility alias for validate_embedding().
    """

    return validate_embedding(
        embedding=embedding,
        expected_dimension=expected_dimension,
    )


# =============================================================================
# Model loader
# =============================================================================

@lru_cache(maxsize=4)
def get_embedding_model(
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> SentenceTransformer:
    """
    Load and cache a SentenceTransformer model.
    """

    resolved_model_name = (
        model_name.strip()
        if model_name and model_name.strip()
        else DEFAULT_EMBEDDING_MODEL
    )

    try:
        logger.info(
            "Loading embedding model: %s",
            resolved_model_name,
        )

        model = SentenceTransformer(
            resolved_model_name
        )

        logger.info(
            "Embedding model loaded successfully: %s",
            resolved_model_name,
        )

        return model

    except Exception as exc:
        logger.exception(
            "Unable to load embedding model: %s",
            resolved_model_name,
        )

        raise EmbeddingServiceError(
            "Unable to load embedding model "
            f"'{resolved_model_name}': {exc}"
        ) from exc


# =============================================================================
# Embedding service
# =============================================================================

class EmbeddingService:
    """
    Generates embeddings for document text, chunks and queries.
    """

    def __init__(
        self,
        *,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
        batch_size: int = DEFAULT_BATCH_SIZE,
        normalize_embeddings: bool = (
            DEFAULT_NORMALIZE_EMBEDDINGS
        ),
    ) -> None:
        if not model_name or not model_name.strip():
            raise ValueError(
                "model_name cannot be empty."
            )

        if batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than zero."
            )

        self.model_name = model_name.strip()
        self.batch_size = batch_size
        self.normalize_embeddings = (
            normalize_embeddings
        )

        self._model: SentenceTransformer | None = None
        self._embedding_dimension: int | None = None

    @property
    def model(self) -> SentenceTransformer:
        """
        Lazily load the embedding model.
        """

        if self._model is None:
            self._model = get_embedding_model(
                self.model_name
            )

        return self._model

    @property
    def embedding_dimension(self) -> int:
        """
        Return the model embedding dimension.

        Required by vector_store.py.
        """

        if self._embedding_dimension is not None:
            return self._embedding_dimension

        try:
            dimension = (
                self.model
                .get_sentence_embedding_dimension()
            )

            if dimension is None:
                dimension = DEFAULT_EMBEDDING_DIMENSION

            self._embedding_dimension = int(
                dimension
            )

            return self._embedding_dimension

        except Exception as exc:
            logger.warning(
                "Unable to read model embedding dimension: %s",
                exc,
            )

            self._embedding_dimension = (
                DEFAULT_EMBEDDING_DIMENSION
            )

            return self._embedding_dimension

    @property
    def vector_dimension(self) -> int:
        """
        Compatibility property.
        """

        return self.embedding_dimension

    def embed_text(
        self,
        text: str,
    ) -> list[float]:
        """
        Generate an embedding for one text value.
        """

        cleaned_text = _clean_text(text)

        try:
            embedding = self.model.encode(
                cleaned_text,
                convert_to_numpy=True,
                normalize_embeddings=(
                    self.normalize_embeddings
                ),
                show_progress_bar=False,
            )

            vector = _embedding_to_list(
                embedding
            )

            validate_embedding(
                embedding=vector,
                expected_dimension=(
                    self.embedding_dimension
                ),
            )

            return vector

        except EmbeddingServiceError:
            raise

        except Exception as exc:
            logger.exception(
                "Unable to generate embedding."
            )

            raise EmbeddingServiceError(
                f"Unable to generate embedding: {exc}"
            ) from exc

    def embed_texts(
        self,
        texts: Iterable[str],
        *,
        batch_size: int | None = None,
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple text values.
        """

        cleaned_texts = _clean_texts(texts)

        resolved_batch_size = (
            batch_size
            if batch_size is not None
            else self.batch_size
        )

        if resolved_batch_size <= 0:
            raise ValueError(
                "batch_size must be greater than zero."
            )

        try:
            embeddings = self.model.encode(
                cleaned_texts,
                batch_size=resolved_batch_size,
                convert_to_numpy=True,
                normalize_embeddings=(
                    self.normalize_embeddings
                ),
                show_progress_bar=False,
            )

            vectors = [
                _embedding_to_list(embedding)
                for embedding in embeddings
            ]

            if len(vectors) != len(cleaned_texts):
                raise InvalidEmbeddingError(
                    "Generated embedding count does not "
                    "match the number of input texts."
                )

            for vector in vectors:
                validate_embedding(
                    embedding=vector,
                    expected_dimension=(
                        self.embedding_dimension
                    ),
                )

            logger.info(
                "Generated %s embeddings using model %s.",
                len(vectors),
                self.model_name,
            )

            return vectors

        except EmbeddingServiceError:
            raise

        except Exception as exc:
            logger.exception(
                "Unable to generate batch embeddings."
            )

            raise EmbeddingServiceError(
                "Unable to generate batch embeddings: "
                f"{exc}"
            ) from exc

    def generate_embedding(
        self,
        text: str,
    ) -> list[float]:
        """
        Compatibility method.
        """

        return self.embed_text(text)

    def generate_embeddings(
        self,
        texts: Iterable[str],
        *,
        batch_size: int | None = None,
    ) -> list[list[float]]:
        """
        Compatibility method.
        """

        return self.embed_texts(
            texts,
            batch_size=batch_size,
        )

    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        """
        Generate an embedding for a search query.
        """

        return self.embed_text(query)

    def embed_documents(
        self,
        documents: Iterable[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for document texts.
        """

        return self.embed_texts(documents)

    def embed_chunks(
        self,
        chunks: Sequence[Any],
    ) -> list[dict[str, Any]]:
        """
        Embed DocumentChunk objects and prepare them for VectorStore.

        Expected chunk attributes:
        - chunk_index
        - content
        - metadata
        """

        if not chunks:
            raise EmptyEmbeddingInputError(
                "At least one document chunk is required."
            )

        texts: list[str] = []

        for index, chunk in enumerate(chunks):
            content = getattr(
                chunk,
                "content",
                None,
            )

            if not isinstance(content, str):
                raise InvalidEmbeddingError(
                    f"Chunk at position {index} "
                    "does not contain valid content."
                )

            texts.append(
                _clean_text(content)
            )

        vectors = self.embed_texts(
            texts
        )

        embedded_chunks: list[
            dict[str, Any]
        ] = []

        for chunk, vector in zip(
            chunks,
            vectors,
        ):
            metadata = dict(
                getattr(
                    chunk,
                    "metadata",
                    {},
                )
                or {}
            )

            chunk_index = int(
                getattr(
                    chunk,
                    "chunk_index",
                    len(embedded_chunks),
                )
            )

            document_id = metadata.get(
                "document_id"
            )

            if not document_id:
                raise InvalidEmbeddingError(
                    "Chunk metadata must contain "
                    "'document_id'."
                )

            vector_id = (
                f"{document_id}:{chunk_index}"
            )

            metadata.update(
                {
                    "document_id": str(
                        document_id
                    ),
                    "chunk_index": chunk_index,
                    "embedding_model": (
                        self.model_name
                    ),
                    "vector_dimension": (
                        self.embedding_dimension
                    ),
                    "vector_id": vector_id,
                }
            )

            embedded_chunks.append(
                {
                    "id": vector_id,
                    "document": chunk.content,
                    "embedding": vector,
                    "metadata": metadata,
                }
            )

        return embedded_chunks


# =============================================================================
# Cached embedding service
# =============================================================================

@lru_cache(maxsize=4)
def get_embedding_service(
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    batch_size: int = DEFAULT_BATCH_SIZE,
    normalize_embeddings: bool = (
        DEFAULT_NORMALIZE_EMBEDDINGS
    ),
) -> EmbeddingService:
    """
    Return a cached EmbeddingService instance.
    """

    return EmbeddingService(
        model_name=model_name,
        batch_size=batch_size,
        normalize_embeddings=normalize_embeddings,
    )


# =============================================================================
# Function-based API
# =============================================================================

def generate_embedding(
    text: str,
    model_name: str = DEFAULT_EMBEDDING_MODEL,
) -> list[float]:
    """
    Generate an embedding for one text value.
    """

    service = get_embedding_service(
        model_name=model_name
    )

    return service.generate_embedding(
        text
    )


def generate_embeddings(
    texts: Iterable[str],
    model_name: str = DEFAULT_EMBEDDING_MODEL,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> list[list[float]]:
    """
    Generate embeddings for multiple text values.
    """

    service = get_embedding_service(
        model_name=model_name,
        batch_size=batch_size,
    )

    return service.generate_embeddings(
        texts,
        batch_size=batch_size,
    )


# =============================================================================
# Similarity utility
# =============================================================================

def cosine_similarity(
    vector_a: Sequence[float],
    vector_b: Sequence[float],
) -> float:
    """
    Calculate cosine similarity between two vectors.
    """

    validate_embedding(vector_a)
    validate_embedding(vector_b)

    if len(vector_a) != len(vector_b):
        raise InvalidEmbeddingError(
            "Vectors must have the same dimension."
        )

    array_a = np.asarray(
        vector_a,
        dtype=np.float32,
    )

    array_b = np.asarray(
        vector_b,
        dtype=np.float32,
    )

    denominator = (
        np.linalg.norm(array_a)
        * np.linalg.norm(array_b)
    )

    if denominator == 0:
        return 0.0

    similarity = np.dot(
        array_a,
        array_b,
    ) / denominator

    return float(similarity)
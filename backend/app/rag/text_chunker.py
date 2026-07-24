from __future__ import annotations

import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TextChunk:
    """
    Represents one text chunk created from a document.
    """

    chunk_index: int
    content: str
    start_character: int
    end_character: int
    character_count: int
    word_count: int
    metadata: dict


def clean_text_for_chunking(text: str) -> str:
    """
    Normalize text before splitting it into chunks.
    """

    if not text:
        return ""

    cleaned = text.replace("\x00", "")

    cleaned = cleaned.replace("\r\n", "\n")
    cleaned = cleaned.replace("\r", "\n")

    cleaned = re.sub(
        r"[ \t]+",
        " ",
        cleaned,
    )

    cleaned = re.sub(
        r" *\n *",
        "\n",
        cleaned,
    )

    cleaned = re.sub(
        r"\n{3,}",
        "\n\n",
        cleaned,
    )

    return cleaned.strip()


def count_words(text: str) -> int:
    """
    Count words in a text string.
    """

    if not text:
        return 0

    return len(
        re.findall(
            r"\b\w+\b",
            text,
        )
    )


def find_best_split_position(
    text: str,
    start: int,
    target_end: int,
    minimum_end: int,
) -> int:
    """
    Find a natural split position near the desired chunk boundary.

    Priority:
    1. Paragraph boundary
    2. Line boundary
    3. Sentence boundary
    4. Space boundary
    5. Exact target position
    """

    if target_end >= len(text):
        return len(text)

    search_region = text[minimum_end:target_end]

    if not search_region:
        return target_end

    paragraph_position = search_region.rfind("\n\n")

    if paragraph_position != -1:
        return minimum_end + paragraph_position + 2

    line_position = search_region.rfind("\n")

    if line_position != -1:
        return minimum_end + line_position + 1

    sentence_positions = [
        search_region.rfind(". "),
        search_region.rfind("? "),
        search_region.rfind("! "),
    ]

    sentence_position = max(sentence_positions)

    if sentence_position != -1:
        return minimum_end + sentence_position + 2

    space_position = search_region.rfind(" ")

    if space_position != -1:
        return minimum_end + space_position + 1

    return target_end


def split_text_into_chunks(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    document_id: str | None = None,
    source_name: str | None = None,
    extra_metadata: dict | None = None,
) -> list[TextChunk]:
    """
    Split extracted text into overlapping chunks.

    Args:
        text:
            Complete extracted document text.

        chunk_size:
            Maximum number of characters in each chunk.

        chunk_overlap:
            Number of characters repeated between consecutive chunks.

        document_id:
            Optional document ID added to chunk metadata.

        source_name:
            Optional original filename added to chunk metadata.

        extra_metadata:
            Additional metadata copied to every chunk.

    Returns:
        List of TextChunk objects.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than zero.")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative.")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size.")

    cleaned_text = clean_text_for_chunking(text)

    if not cleaned_text:
        return []

    chunks: list[TextChunk] = []

    text_length = len(cleaned_text)

    start = 0
    chunk_index = 0

    while start < text_length:
        target_end = min(
            start + chunk_size,
            text_length,
        )

        minimum_chunk_size = max(
            int(chunk_size * 0.6),
            1,
        )

        minimum_end = min(
            start + minimum_chunk_size,
            target_end,
        )

        end = find_best_split_position(
            text=cleaned_text,
            start=start,
            target_end=target_end,
            minimum_end=minimum_end,
        )

        if end <= start:
            end = target_end

        chunk_content = cleaned_text[start:end].strip()

        if chunk_content:
            metadata = {
                "chunk_index": chunk_index,
                "start_character": start,
                "end_character": end,
            }

            if document_id is not None:
                metadata["document_id"] = str(document_id)

            if source_name is not None:
                metadata["source_name"] = source_name

            if extra_metadata:
                metadata.update(extra_metadata)

            chunk = TextChunk(
                chunk_index=chunk_index,
                content=chunk_content,
                start_character=start,
                end_character=end,
                character_count=len(chunk_content),
                word_count=count_words(chunk_content),
                metadata=metadata,
            )

            chunks.append(chunk)

            chunk_index += 1

        if end >= text_length:
            break

        next_start = end - chunk_overlap

        if next_start <= start:
            next_start = end

        start = next_start

    logger.info(
        "Created %s chunks from %s characters.",
        len(chunks),
        text_length,
    )

    return chunks


def chunks_to_dicts(
    chunks: list[TextChunk],
) -> list[dict]:
    """
    Convert TextChunk objects into dictionaries.
    """

    return [
        {
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "start_character": chunk.start_character,
            "end_character": chunk.end_character,
            "character_count": chunk.character_count,
            "word_count": chunk.word_count,
            "metadata": chunk.metadata,
        }
        for chunk in chunks
    ]

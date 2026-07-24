import hashlib
import json
from typing import Any


def generate_cache_key(
    prefix: str,
    data: Any,
) -> str:
    """Generate a stable Redis cache key from request data."""

    serialized_data = json.dumps(
        data,
        sort_keys=True,
        default=str,
    )

    digest = hashlib.sha256(
        serialized_data.encode("utf-8")
    ).hexdigest()

    return f"{prefix}:{digest}"


def chat_cache_key(
    user_id: int | str,
    message: str,
) -> str:
    return generate_cache_key(
        prefix="chat",
        data={
            "user_id": user_id,
            "message": message.strip().lower(),
        },
    )


def rag_cache_key(
    query: str,
    document_id: int | str | None = None,
) -> str:
    return generate_cache_key(
        prefix="rag",
        data={
            "query": query.strip().lower(),
            "document_id": document_id,
        },
    )
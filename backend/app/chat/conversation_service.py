from datetime import datetime, timezone
from math import ceil
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.chat.models import (
    Conversation,
    Message,
    MessageRole,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def create_conversation(
    db: Session,
    user_id: int,
    title: str = "New Conversation",
) -> Conversation:
    conversation = Conversation(
        user_id=user_id,
        title=title.strip() or "New Conversation",
    )

    db.add(conversation)
    db.flush()

    return conversation


def generate_conversation_title(
    prompt: str,
    max_length: int = 60,
) -> str:
    """
    Generate a short title from the first user prompt.
    """

    cleaned_prompt = " ".join(
        prompt.strip().split()
    )

    if len(cleaned_prompt) <= max_length:
        return cleaned_prompt

    return (
        cleaned_prompt[: max_length - 3].rstrip()
        + "..."
    )


def get_user_conversation(
    db: Session,
    conversation_id: UUID,
    user_id: int,
    *,
    include_messages: bool = False,
) -> Conversation:
    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id,
    )

    if include_messages:
        statement = statement.options(
            selectinload(
                Conversation.messages
            )
        )

    conversation = db.scalar(statement)

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return conversation


def add_message(
    db: Session,
    conversation_id: UUID,
    role: MessageRole,
    content: str,
    *,
    token_count: int = 0,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    provider: str | None = None,
    model_name: str | None = None,
) -> Message:
    cleaned_content = content.strip()

    if not cleaned_content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message content cannot be empty",
        )

    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=cleaned_content,
        token_count=max(token_count, 0),
        prompt_tokens=max(prompt_tokens, 0),
        completion_tokens=max(
            completion_tokens,
            0,
        ),
        provider=provider,
        model_name=model_name,
    )

    db.add(message)

    conversation = db.get(
        Conversation,
        conversation_id,
    )

    if conversation is not None:
        conversation.updated_at = utc_now()

    db.flush()

    return message


def get_conversation_messages(
    db: Session,
    conversation_id: UUID,
    user_id: int,
) -> list[Message]:
    get_user_conversation(
        db,
        conversation_id,
        user_id,
    )

    statement = (
        select(Message)
        .where(
            Message.conversation_id
            == conversation_id
        )
        .order_by(
            Message.created_at.asc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


def list_conversations(
    db: Session,
    user_id: int,
    *,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    archived: bool = False,
) -> dict:
    filters = [
        Conversation.user_id == user_id,
        Conversation.is_archived == archived,
    ]

    if search and search.strip():
        filters.append(
            Conversation.title.ilike(
                f"%{search.strip()}%"
            )
        )

    total_statement = (
        select(func.count(Conversation.id))
        .where(*filters)
    )

    total = db.scalar(total_statement) or 0

    statement = (
        select(Conversation)
        .where(*filters)
        .order_by(
            Conversation.is_pinned.desc(),
            Conversation.updated_at.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    conversations = list(
        db.scalars(statement).all()
    )

    return {
        "items": conversations,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (
            ceil(total / page_size)
            if total
            else 0
        ),
    }


def rename_conversation(
    db: Session,
    conversation_id: UUID,
    user_id: int,
    title: str,
) -> Conversation:
    conversation = get_user_conversation(
        db,
        conversation_id,
        user_id,
    )

    cleaned_title = title.strip()

    if not cleaned_title:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Conversation title cannot be empty",
        )

    conversation.title = cleaned_title
    conversation.updated_at = utc_now()

    db.flush()

    return conversation


def delete_conversation(
    db: Session,
    conversation_id: UUID,
    user_id: int,
) -> None:
    conversation = get_user_conversation(
        db,
        conversation_id,
        user_id,
    )

    db.delete(conversation)
    db.flush()

def archive_conversation(
    db: Session,
    conversation_id: UUID,
    user_id: int,
):
    conversation = get_user_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=user_id,
    )

    conversation.is_archived = True
    conversation.archived_at = datetime.now(
        timezone.utc
    )

    db.flush()

    return conversation


def restore_conversation(
    db: Session,
    conversation_id: UUID,
    user_id: int,
):
    conversation = get_user_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=user_id,
    )

    conversation.is_archived = False
    conversation.archived_at = None

    db.flush()

    return conversation
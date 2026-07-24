from __future__ import annotations

from datetime import UTC, datetime
from math import ceil
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.chat.models import (
    Conversation,
    Message,
    MessageRole,
)


def utc_now() -> datetime:
    """Return the current timezone-aware UTC datetime."""
    return datetime.now(UTC)


def create_conversation(
    db: Session,
    user_id: int,
    title: str = "New Conversation",
) -> Conversation:
    """
    Create and flush a new conversation.

    The caller is responsible for committing the transaction.
    """

    cleaned_title = title.strip() or "New Conversation"

    conversation = Conversation(
        user_id=user_id,
        title=cleaned_title,
        is_archived=False,
        is_pinned=False,
        total_tokens=0,
    )

    db.add(conversation)

    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Unable to create the conversation because its database relationships are invalid."
            ),
        ) from exc

    # Ensure SQLAlchemy has generated the UUID primary key.
    if conversation.id is None:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Conversation UUID was not generated",
        )

    return conversation


def generate_conversation_title(
    prompt: str,
    max_length: int = 60,
) -> str:
    """Generate a short title from the first user prompt."""

    cleaned_prompt = " ".join(prompt.strip().split())

    if not cleaned_prompt:
        return "New Conversation"

    if len(cleaned_prompt) <= max_length:
        return cleaned_prompt

    return cleaned_prompt[: max_length - 3].rstrip() + "..."


def get_user_conversation(
    db: Session,
    conversation_id: UUID,
    user_id: int,
    *,
    include_messages: bool = False,
) -> Conversation:
    """
    Return a conversation owned by the specified user.
    """

    statement = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id,
    )

    if include_messages:
        statement = statement.options(selectinload(Conversation.messages))

    conversation = db.scalar(statement)

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    return conversation


def get_conversation_by_id(
    db: Session,
    conversation_id: UUID,
) -> Conversation:
    """
    Return a conversation without applying a user filter.

    This is used internally before creating messages.
    """

    statement = select(Conversation).where(Conversation.id == conversation_id)

    conversation = db.scalar(statement)

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=("Cannot add a message because the conversation does not exist."),
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
    """
    Add a message to an existing conversation.

    The relationship is assigned directly so SQLAlchemy preserves
    the correct insertion order between Conversation and Message.
    """

    cleaned_content = content.strip()

    if not cleaned_content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message content cannot be empty",
        )

    # Query the parent row before inserting the child row.
    conversation = get_conversation_by_id(
        db=db,
        conversation_id=conversation_id,
    )

    message = Message(
        conversation=conversation,
        role=role,
        content=cleaned_content,
        token_count=max(token_count, 0),
        prompt_tokens=max(prompt_tokens, 0),
        completion_tokens=max(completion_tokens, 0),
        provider=provider,
        model_name=model_name,
    )

    # Append through the ORM relationship.
    conversation.messages.append(message)

    conversation.updated_at = utc_now()

    if role == MessageRole.ASSISTANT:
        conversation.total_tokens = max(conversation.total_tokens, 0) + max(token_count, 0)

    db.add(message)

    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("The message could not be saved because its conversation no longer exists."),
        ) from exc

    return message


def get_conversation_messages(
    db: Session,
    conversation_id: UUID,
    user_id: int,
) -> list[Message]:
    """Return all messages belonging to a user conversation."""

    get_user_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=user_id,
    )

    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )

    return list(db.scalars(statement).all())


def list_conversations(
    db: Session,
    user_id: int,
    *,
    page: int = 1,
    page_size: int = 20,
    search: str | None = None,
    archived: bool = False,
) -> dict:
    """Return paginated conversations for one user."""

    filters = [
        Conversation.user_id == user_id,
        Conversation.is_archived == archived,
    ]

    if search and search.strip():
        filters.append(Conversation.title.ilike(f"%{search.strip()}%"))

    total_statement = select(func.count(Conversation.id)).where(*filters)

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

    conversations = list(db.scalars(statement).all())

    return {
        "items": conversations,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": (ceil(total / page_size) if total else 0),
    }


def rename_conversation(
    db: Session,
    conversation_id: UUID,
    user_id: int,
    title: str,
) -> Conversation:
    """Rename an existing conversation."""

    conversation = get_user_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=user_id,
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
    """Delete a conversation and its child messages."""

    conversation = get_user_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=user_id,
    )

    db.delete(conversation)
    db.flush()


def archive_conversation(
    db: Session,
    conversation_id: UUID,
    user_id: int,
) -> Conversation:
    """Archive an existing conversation."""

    conversation = get_user_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=user_id,
    )

    conversation.is_archived = True
    conversation.archived_at = utc_now()
    conversation.updated_at = utc_now()

    db.flush()

    return conversation


def restore_conversation(
    db: Session,
    conversation_id: UUID,
    user_id: int,
) -> Conversation:
    """Restore an archived conversation."""

    conversation = get_user_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=user_id,
    )

    conversation.is_archived = False
    conversation.archived_at = None
    conversation.updated_at = utc_now()

    db.flush()

    return conversation

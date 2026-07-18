from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.chat.models import PromptStatus, PromptTemplate
from app.chat.prompt_schemas import (
    PromptTemplateCreate,
    PromptTemplateUpdate,
)


class PromptTemplateNotFoundError(Exception):
    """Raised when a prompt template does not exist."""


class PromptTemplatePermissionError(Exception):
    """Raised when a user cannot access or modify a template."""


def create_prompt_template(
    db: Session,
    user_id: int,
    payload: PromptTemplateCreate,
) -> PromptTemplate:
    """
    Create a new prompt template for the authenticated user.
    """

    template = PromptTemplate(
        user_id=user_id,
        name=payload.name.strip(),
        description=(
            payload.description.strip()
            if payload.description
            else None
        ),
        content=payload.content.strip(),
        category=(
            payload.category.strip()
            if payload.category
            else None
        ),
        status=payload.status,
        is_public=payload.is_public,
        usage_count=0,
    )

    db.add(template)

    try:
        db.commit()
        db.refresh(template)
    except Exception:
        db.rollback()
        raise

    return template


def get_prompt_template(
    db: Session,
    template_id: UUID,
    user_id: int,
) -> PromptTemplate:
    """
    Return a template when it belongs to the user or is public.
    """

    statement = (
        select(PromptTemplate)
        .where(PromptTemplate.id == template_id)
        .where(
            or_(
                PromptTemplate.user_id == user_id,
                PromptTemplate.is_public.is_(True),
            )
        )
    )

    template = db.scalar(statement)

    if template is None:
        raise PromptTemplateNotFoundError(
            "Prompt template was not found or you do not have access."
        )

    return template


def get_owned_prompt_template(
    db: Session,
    template_id: UUID,
    user_id: int,
) -> PromptTemplate:
    """
    Return a template only when it belongs to the user.

    This function is used for update and delete operations.
    """

    statement = select(PromptTemplate).where(
        PromptTemplate.id == template_id
    )

    template = db.scalar(statement)

    if template is None:
        raise PromptTemplateNotFoundError(
            "Prompt template was not found."
        )

    if template.user_id != user_id:
        raise PromptTemplatePermissionError(
            "You do not have permission to modify this template."
        )

    return template


def list_prompt_templates(
    db: Session,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
    category: str | None = None,
    status: PromptStatus | None = None,
    search: str | None = None,
    include_public: bool = True,
) -> tuple[list[PromptTemplate], int]:
    """
    List templates owned by the user and optionally public templates.
    """

    conditions = []

    if include_public:
        conditions.append(
            or_(
                PromptTemplate.user_id == user_id,
                PromptTemplate.is_public.is_(True),
            )
        )
    else:
        conditions.append(
            PromptTemplate.user_id == user_id
        )

    if category:
        conditions.append(
            func.lower(PromptTemplate.category)
            == category.strip().lower()
        )

    if status:
        conditions.append(
            PromptTemplate.status == status
        )

    if search:
        search_value = f"%{search.strip()}%"

        conditions.append(
            or_(
                PromptTemplate.name.ilike(search_value),
                PromptTemplate.description.ilike(search_value),
                PromptTemplate.content.ilike(search_value),
                PromptTemplate.category.ilike(search_value),
            )
        )

    count_statement = (
        select(func.count(PromptTemplate.id))
        .where(*conditions)
    )

    total = db.scalar(count_statement) or 0

    offset = (page - 1) * page_size

    statement = (
        select(PromptTemplate)
        .where(*conditions)
        .order_by(
            PromptTemplate.updated_at.desc(),
            PromptTemplate.created_at.desc(),
        )
        .offset(offset)
        .limit(page_size)
    )

    templates = list(
        db.scalars(statement).all()
    )

    return templates, total


def update_prompt_template(
    db: Session,
    template_id: UUID,
    user_id: int,
    payload: PromptTemplateUpdate,
) -> PromptTemplate:
    """
    Update a prompt template owned by the authenticated user.
    """

    template = get_owned_prompt_template(
        db=db,
        template_id=template_id,
        user_id=user_id,
    )

    update_data = payload.model_dump(
        exclude_unset=True
    )

    if (
        "name" in update_data
        and update_data["name"] is not None
    ):
        update_data["name"] = (
            update_data["name"].strip()
        )

    if (
        "description" in update_data
        and update_data["description"] is not None
    ):
        update_data["description"] = (
            update_data["description"].strip()
        )

    if (
        "content" in update_data
        and update_data["content"] is not None
    ):
        update_data["content"] = (
            update_data["content"].strip()
        )

    if (
        "category" in update_data
        and update_data["category"] is not None
    ):
        update_data["category"] = (
            update_data["category"].strip()
        )

    for field_name, value in update_data.items():
        setattr(template, field_name, value)

    try:
        db.commit()
        db.refresh(template)
    except Exception:
        db.rollback()
        raise

    return template


def delete_prompt_template(
    db: Session,
    template_id: UUID,
    user_id: int,
) -> None:
    """
    Delete a prompt template owned by the authenticated user.
    """

    template = get_owned_prompt_template(
        db=db,
        template_id=template_id,
        user_id=user_id,
    )

    db.delete(template)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise


def increment_prompt_template_usage(
    db: Session,
    template_id: UUID,
    user_id: int,
) -> PromptTemplate:
    """
    Increase the usage count through the dedicated /use endpoint.
    """

    template = get_prompt_template(
        db=db,
        template_id=template_id,
        user_id=user_id,
    )

    template.usage_count = (
        template.usage_count or 0
    ) + 1

    try:
        db.commit()
        db.refresh(template)
    except Exception:
        db.rollback()
        raise

    return template


def render_prompt_template(
    db: Session,
    template_id: UUID,
    user_id: int,
    question: str,
) -> str:
    """
    Load, validate and render a prompt template for AI chat.

    Supported placeholders:

    {question}
    {prompt}

    If the template does not contain either placeholder,
    the user's question is appended to the template.
    """

    template = get_prompt_template(
        db=db,
        template_id=template_id,
        user_id=user_id,
    )

    if template.status != PromptStatus.ACTIVE:
        raise PromptTemplatePermissionError(
            "This prompt template is not active."
        )

    clean_question = question.strip()
    template_content = template.content.strip()

    contains_question_placeholder = (
        "{question}" in template_content
    )

    contains_prompt_placeholder = (
        "{prompt}" in template_content
    )

    rendered_prompt = template_content.replace(
        "{question}",
        clean_question,
    )

    rendered_prompt = rendered_prompt.replace(
        "{prompt}",
        clean_question,
    )

    if not (
        contains_question_placeholder
        or contains_prompt_placeholder
    ):
        rendered_prompt = (
            f"{template_content}\n\n"
            f"User question:\n{clean_question}"
        )

    template.usage_count = (
        template.usage_count or 0
    ) + 1

    # Do not commit here.
    # The chat endpoint commits the complete chat transaction.
    db.flush()

    return rendered_prompt
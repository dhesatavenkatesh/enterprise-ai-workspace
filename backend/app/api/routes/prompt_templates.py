from __future__ import annotations

from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.chat.models import PromptStatus
from app.chat.prompt_schemas import (
    PromptTemplateCreate,
    PromptTemplateDeleteResponse,
    PromptTemplateListResponse,
    PromptTemplateResponse,
    PromptTemplateUpdate,
    PromptTemplateUseResponse,
)
from app.chat.prompt_service import (
    PromptTemplateNotFoundError,
    PromptTemplatePermissionError,
    create_prompt_template,
    delete_prompt_template,
    get_prompt_template,
    increment_prompt_template_usage,
    list_prompt_templates,
    update_prompt_template,
)
from app.database.session import get_db
from app.models.user import User

router = APIRouter(
    prefix="/api/prompt-templates",
    tags=["Prompt Templates"],
)


def handle_prompt_template_error(exc: Exception) -> None:
    if isinstance(exc, PromptTemplateNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    if isinstance(exc, PromptTemplatePermissionError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    raise exc


@router.post(
    "",
    response_model=PromptTemplateResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_template(
    payload: PromptTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PromptTemplateResponse:
    template = create_prompt_template(
        db=db,
        user_id=current_user.id,
        payload=payload,
    )

    return PromptTemplateResponse.model_validate(template)


@router.get(
    "",
    response_model=PromptTemplateListResponse,
)
def get_templates(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category: str | None = Query(default=None),
    template_status: PromptStatus | None = Query(
        default=None,
        alias="status",
    ),
    search: str | None = Query(default=None, max_length=200),
    include_public: bool = Query(default=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PromptTemplateListResponse:
    templates, total = list_prompt_templates(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        category=category,
        status=template_status,
        search=search,
        include_public=include_public,
    )

    return PromptTemplateListResponse(
        items=[PromptTemplateResponse.model_validate(template) for template in templates],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{template_id}",
    response_model=PromptTemplateResponse,
)
def get_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PromptTemplateResponse:
    try:
        template = get_prompt_template(
            db=db,
            template_id=template_id,
            user_id=current_user.id,
        )
    except (
        PromptTemplateNotFoundError,
        PromptTemplatePermissionError,
    ) as exc:
        handle_prompt_template_error(exc)

    return PromptTemplateResponse.model_validate(template)


@router.put(
    "/{template_id}",
    response_model=PromptTemplateResponse,
)
def update_template(
    template_id: UUID,
    payload: PromptTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PromptTemplateResponse:
    try:
        template = update_prompt_template(
            db=db,
            template_id=template_id,
            user_id=current_user.id,
            payload=payload,
        )
    except (
        PromptTemplateNotFoundError,
        PromptTemplatePermissionError,
    ) as exc:
        handle_prompt_template_error(exc)

    return PromptTemplateResponse.model_validate(template)


@router.delete(
    "/{template_id}",
    response_model=PromptTemplateDeleteResponse,
)
def delete_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PromptTemplateDeleteResponse:
    try:
        delete_prompt_template(
            db=db,
            template_id=template_id,
            user_id=current_user.id,
        )
    except (
        PromptTemplateNotFoundError,
        PromptTemplatePermissionError,
    ) as exc:
        handle_prompt_template_error(exc)

    return PromptTemplateDeleteResponse(
        message="Prompt template deleted successfully.",
        template_id=template_id,
    )


@router.post(
    "/{template_id}/use",
    response_model=PromptTemplateUseResponse,
)
def use_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PromptTemplateUseResponse:
    try:
        template = increment_prompt_template_usage(
            db=db,
            template_id=template_id,
            user_id=current_user.id,
        )
    except (
        PromptTemplateNotFoundError,
        PromptTemplatePermissionError,
    ) as exc:
        handle_prompt_template_error(exc)

    return PromptTemplateUseResponse(
        message="Prompt template usage recorded successfully.",
        template_id=template.id,
        usage_count=template.usage_count,
    )

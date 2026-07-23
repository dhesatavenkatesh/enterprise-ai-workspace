from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
)
from sqlalchemy.orm import Session

from app.admin.audit.utils import get_client_ip
from app.admin.users.schemas import (
    AdminPasswordReset,
    AdminUserActionResponse,
    AdminUserCreate,
    AdminUserDeleteResponse,
    AdminUserListResponse,
    AdminUserResponse,
    AdminUserStatusUpdate,
    AdminUserUpdate,
)
from app.admin.users.service import (
    activate_user,
    create_user,
    deactivate_user,
    get_user,
    list_users,
    lock_user,
    reset_user_password,
    soft_delete_user,
    unlock_user,
    update_user,
    update_user_status,
)
from app.api.dependencies.rbac import require_admin
from app.database.session import get_db
from app.models.user import User


router = APIRouter(
    prefix="/users",
    tags=["Sprint 5 - Admin Users"],
)


DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]

AdminUser = Annotated[
    User,
    Depends(require_admin),
]


@router.get(
    "",
    response_model=AdminUserListResponse,
    summary="List admin users",
)
def get_admin_users(
    db: DatabaseSession,
    current_user: AdminUser,
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    search: str | None = Query(
        default=None,
        max_length=100,
    ),
    role_id: int | None = Query(
        default=None,
        gt=0,
    ),
    user_status: str | None = Query(
        default=None,
        alias="status",
    ),
    is_active: bool | None = Query(
        default=None,
    ),
    is_locked: bool | None = Query(
        default=None,
    ),
    include_deleted: bool = Query(
        default=False,
    ),
) -> AdminUserListResponse:
    return list_users(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        role_id=role_id,
        user_status=user_status,
        is_active=is_active,
        is_locked=is_locked,
        include_deleted=include_deleted,
    )


@router.post(
    "",
    response_model=AdminUserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create admin user",
)
def create_admin_user(
    payload: AdminUserCreate,
    request: Request,
    db: DatabaseSession,
    current_user: AdminUser,
) -> AdminUserResponse:
    return create_user(
        db=db,
        request=payload,
        admin_user_id=current_user.id,
        ip_address=get_client_ip(request),
    )


@router.get(
    "/{user_id}",
    response_model=AdminUserResponse,
    summary="Get admin user",
)
def get_admin_user(
    user_id: int,
    db: DatabaseSession,
    current_user: AdminUser,
) -> AdminUserResponse:
    return get_user(
        db=db,
        user_id=user_id,
    )


@router.put(
    "/{user_id}",
    response_model=AdminUserResponse,
    summary="Update admin user",
)
def update_admin_user(
    user_id: int,
    payload: AdminUserUpdate,
    request: Request,
    db: DatabaseSession,
    current_user: AdminUser,
) -> AdminUserResponse:
    return update_user(
        db=db,
        user_id=user_id,
        request=payload,
        admin_user_id=current_user.id,
        ip_address=get_client_ip(request),
    )


@router.patch(
    "/{user_id}/status",
    response_model=AdminUserResponse,
    summary="Update user active status",
)
def change_user_status(
    user_id: int,
    payload: AdminUserStatusUpdate,
    request: Request,
    db: DatabaseSession,
    current_user: AdminUser,
) -> AdminUserResponse:
    if (
        current_user.id == user_id
        and payload.is_active is False
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account",
        )

    return update_user_status(
        db=db,
        user_id=user_id,
        is_active=payload.is_active,
        admin_user_id=current_user.id,
        ip_address=get_client_ip(request),
    )


@router.post(
    "/{user_id}/activate",
    response_model=AdminUserActionResponse,
    summary="Activate user",
)
def activate_admin_user(
    user_id: int,
    request: Request,
    db: DatabaseSession,
    current_user: AdminUser,
) -> AdminUserActionResponse:
    user = activate_user(
        db=db,
        user_id=user_id,
        admin_user_id=current_user.id,
        ip_address=get_client_ip(request),
    )

    return AdminUserActionResponse(
        message="User activated successfully",
        user=user,
    )


@router.post(
    "/{user_id}/deactivate",
    response_model=AdminUserActionResponse,
    summary="Deactivate user",
)
def deactivate_admin_user(
    user_id: int,
    request: Request,
    db: DatabaseSession,
    current_user: AdminUser,
) -> AdminUserActionResponse:
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account",
        )

    user = deactivate_user(
        db=db,
        user_id=user_id,
        admin_user_id=current_user.id,
        ip_address=get_client_ip(request),
    )

    return AdminUserActionResponse(
        message="User deactivated successfully",
        user=user,
    )


@router.post(
    "/{user_id}/lock",
    response_model=AdminUserActionResponse,
    summary="Lock user",
)
def lock_admin_user(
    user_id: int,
    request: Request,
    db: DatabaseSession,
    current_user: AdminUser,
) -> AdminUserActionResponse:
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot lock your own account",
        )

    user = lock_user(
        db=db,
        user_id=user_id,
        admin_user_id=current_user.id,
        ip_address=get_client_ip(request),
    )

    return AdminUserActionResponse(
        message="User locked successfully",
        user=user,
    )


@router.post(
    "/{user_id}/unlock",
    response_model=AdminUserActionResponse,
    summary="Unlock user",
)
def unlock_admin_user(
    user_id: int,
    request: Request,
    db: DatabaseSession,
    current_user: AdminUser,
) -> AdminUserActionResponse:
    user = unlock_user(
        db=db,
        user_id=user_id,
        admin_user_id=current_user.id,
        ip_address=get_client_ip(request),
    )

    return AdminUserActionResponse(
        message="User unlocked successfully",
        user=user,
    )


@router.post(
    "/{user_id}/reset-password",
    response_model=AdminUserActionResponse,
    summary="Reset user password",
)
def reset_admin_user_password(
    user_id: int,
    payload: AdminPasswordReset,
    request: Request,
    db: DatabaseSession,
    current_user: AdminUser,
) -> AdminUserActionResponse:
    user = reset_user_password(
        db=db,
        user_id=user_id,
        request=payload,
        admin_user_id=current_user.id,
        ip_address=get_client_ip(request),
    )

    return AdminUserActionResponse(
        message="Password reset successfully",
        user=user,
    )


@router.delete(
    "/{user_id}",
    response_model=AdminUserDeleteResponse,
    summary="Soft-delete user",
)
def delete_admin_user(
    user_id: int,
    request: Request,
    db: DatabaseSession,
    current_user: AdminUser,
) -> AdminUserDeleteResponse:
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account",
        )

    user = soft_delete_user(
        db=db,
        user_id=user_id,
        admin_user_id=current_user.id,
        ip_address=get_client_ip(request),
    )

    return AdminUserDeleteResponse(
        message="User soft-deleted successfully",
        user_id=user.id,
        is_deleted=user.is_deleted,
    )
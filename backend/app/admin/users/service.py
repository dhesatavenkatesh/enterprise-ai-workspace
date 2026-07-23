from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.admin.audit.logger import create_audit_log
from app.admin.users.schemas import (
    AdminPasswordReset,
    AdminUserCreate,
    AdminUserListItem,
    AdminUserListResponse,
    AdminUserResponse,
    AdminUserUpdate,
    RoleSummary,
)
from app.auth.password import hash_password
from app.models.role import Role
from app.models.user import User


def get_role_or_404(
    db: Session,
    role_id: int,
) -> Role:
    role = db.scalar(
        select(Role).where(
            Role.id == role_id
        )
    )

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} was not found",
        )

    return role


def get_user_or_404(
    db: Session,
    user_id: int,
    include_deleted: bool = False,
) -> User:
    statement = (
        select(User)
        .options(joinedload(User.role))
        .where(User.id == user_id)
    )

    if not include_deleted:
        statement = statement.where(
            User.is_deleted.is_(False)
        )

    user = db.scalar(statement)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} was not found",
        )

    return user


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    return db.scalar(
        select(User).where(
            func.lower(User.email)
            == email.strip().lower()
        )
    )


def build_user_response(
    user: User,
) -> AdminUserResponse:
    role_summary = None

    if user.role is not None:
        role_summary = RoleSummary(
            id=user.role.id,
            name=user.role.name,
            description=user.role.description,
        )

    return AdminUserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role_id=user.role_id,
        role=role_summary,
        status=user.status,
        is_active=user.is_active,
        is_locked=user.is_locked,
        is_deleted=user.is_deleted,
        failed_login_attempts=user.failed_login_attempts,
        last_login_at=user.last_login_at,
        password_changed_at=user.password_changed_at,
        deleted_at=user.deleted_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def create_user(
    db: Session,
    request: AdminUserCreate,
    *,
    admin_user_id: int | None = None,
    ip_address: str | None = None,
) -> AdminUserResponse:
    email = str(request.email).strip().lower()

    if get_user_by_email(db, email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        )

    role = get_role_or_404(
        db=db,
        role_id=request.role_id,
    )

    user = User(
        name=request.name.strip(),
        email=email,
        password_hash=hash_password(request.password),
        role_id=role.id,
        status=(
            "active"
            if request.is_active
            else "inactive"
        ),
        is_active=request.is_active,
        is_locked=False,
        is_deleted=False,
        failed_login_attempts=0,
    )

    try:
        db.add(user)
        db.flush()

        create_audit_log(
            db=db,
            user_id=admin_user_id,
            action="USER_CREATED",
            resource="user",
            resource_id=user.id,
            ip_address=ip_address,
            details={
                "target_user_email": user.email,
                "target_user_name": user.name,
                "role_id": role.id,
                "role_name": role.name,
                "is_active": user.is_active,
            },
        )

        db.commit()
        db.refresh(user)

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this email already exists",
        ) from exc

    user = get_user_or_404(
        db=db,
        user_id=user.id,
    )

    return build_user_response(user)


def list_users(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    role_id: int | None = None,
    user_status: str | None = None,
    is_active: bool | None = None,
    is_locked: bool | None = None,
    include_deleted: bool = False,
) -> AdminUserListResponse:
    filters = []

    if not include_deleted:
        filters.append(
            User.is_deleted.is_(False)
        )

    if search and search.strip():
        search_value = f"%{search.strip()}%"

        filters.append(
            or_(
                User.name.ilike(search_value),
                User.email.ilike(search_value),
            )
        )

    if role_id is not None:
        filters.append(
            User.role_id == role_id
        )

    if user_status is not None:
        filters.append(
            User.status == user_status.strip().lower()
        )

    if is_active is not None:
        filters.append(
            User.is_active.is_(is_active)
        )

    if is_locked is not None:
        filters.append(
            User.is_locked.is_(is_locked)
        )

    total_statement = select(
        func.count(User.id)
    )

    if filters:
        total_statement = total_statement.where(
            *filters
        )

    total = db.scalar(total_statement) or 0

    users_statement = (
        select(User)
        .options(joinedload(User.role))
    )

    if filters:
        users_statement = users_statement.where(
            *filters
        )

    users_statement = (
        users_statement
        .order_by(
            User.created_at.desc(),
            User.id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    users = db.scalars(
        users_statement
    ).unique().all()

    items = [
        AdminUserListItem(
            id=user.id,
            name=user.name,
            email=user.email,
            role_id=user.role_id,
            role_name=(
                user.role.name
                if user.role is not None
                else None
            ),
            status=user.status,
            is_active=user.is_active,
            is_locked=user.is_locked,
            is_deleted=user.is_deleted,
            last_login_at=user.last_login_at,
            created_at=user.created_at,
        )
        for user in users
    ]

    return AdminUserListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(
            math.ceil(total / page_size)
            if total > 0
            else 0
        ),
    )


def get_user(
    db: Session,
    user_id: int,
) -> AdminUserResponse:
    user = get_user_or_404(
        db=db,
        user_id=user_id,
    )

    return build_user_response(user)


def update_user(
    db: Session,
    user_id: int,
    request: AdminUserUpdate,
    *,
    admin_user_id: int | None = None,
    ip_address: str | None = None,
) -> AdminUserResponse:
    user = get_user_or_404(
        db=db,
        user_id=user_id,
    )

    data = request.model_dump(
        exclude_unset=True,
    )

    previous_values: dict[str, Any] = {
        "name": user.name,
        "email": user.email,
        "role_id": user.role_id,
        "is_active": user.is_active,
        "status": user.status,
    }

    if "name" in data:
        user.name = data["name"].strip()

    if "email" in data:
        email = str(data["email"]).strip().lower()
        existing = get_user_by_email(db, email)

        if (
            existing is not None
            and existing.id != user.id
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Another user already uses this email",
            )

        user.email = email

    if "role_id" in data:
        role = get_role_or_404(
            db=db,
            role_id=data["role_id"],
        )

        user.role_id = role.id

    if "is_active" in data:
        user.is_active = data["is_active"]

        if user.is_locked:
            user.status = "locked"
        else:
            user.status = (
                "active"
                if user.is_active
                else "inactive"
            )

    try:
        db.flush()

        create_audit_log(
            db=db,
            user_id=admin_user_id,
            action="USER_UPDATED",
            resource="user",
            resource_id=user.id,
            ip_address=ip_address,
            details={
                "target_user_email": user.email,
                "previous_values": previous_values,
                "new_values": data,
            },
        )

        db.commit()
        db.refresh(user)

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to update user because the data conflicts",
        ) from exc

    user = get_user_or_404(
        db=db,
        user_id=user.id,
    )

    return build_user_response(user)


def update_user_status(
    db: Session,
    user_id: int,
    is_active: bool,
    *,
    admin_user_id: int | None = None,
    ip_address: str | None = None,
) -> AdminUserResponse:
    user = get_user_or_404(
        db=db,
        user_id=user_id,
    )

    previous_status = user.status
    previous_is_active = user.is_active

    user.is_active = is_active

    if user.is_locked:
        user.status = "locked"
    else:
        user.status = (
            "active"
            if is_active
            else "inactive"
        )

    action = (
        "USER_ACTIVATED"
        if is_active
        else "USER_DEACTIVATED"
    )

    create_audit_log(
        db=db,
        user_id=admin_user_id,
        action=action,
        resource="user",
        resource_id=user.id,
        ip_address=ip_address,
        details={
            "target_user_email": user.email,
            "previous_is_active": previous_is_active,
            "new_is_active": user.is_active,
            "previous_status": previous_status,
            "new_status": user.status,
        },
    )

    db.commit()
    db.refresh(user)

    user = get_user_or_404(
        db=db,
        user_id=user.id,
    )

    return build_user_response(user)


def activate_user(
    db: Session,
    user_id: int,
    *,
    admin_user_id: int | None = None,
    ip_address: str | None = None,
) -> AdminUserResponse:
    return update_user_status(
        db=db,
        user_id=user_id,
        is_active=True,
        admin_user_id=admin_user_id,
        ip_address=ip_address,
    )


def deactivate_user(
    db: Session,
    user_id: int,
    *,
    admin_user_id: int | None = None,
    ip_address: str | None = None,
) -> AdminUserResponse:
    return update_user_status(
        db=db,
        user_id=user_id,
        is_active=False,
        admin_user_id=admin_user_id,
        ip_address=ip_address,
    )


def lock_user(
    db: Session,
    user_id: int,
    *,
    admin_user_id: int | None = None,
    ip_address: str | None = None,
) -> AdminUserResponse:
    user = get_user_or_404(
        db=db,
        user_id=user_id,
    )

    previous_status = user.status
    previous_is_locked = user.is_locked

    user.is_locked = True
    user.status = "locked"

    create_audit_log(
        db=db,
        user_id=admin_user_id,
        action="USER_LOCKED",
        resource="user",
        resource_id=user.id,
        ip_address=ip_address,
        details={
            "target_user_email": user.email,
            "previous_is_locked": previous_is_locked,
            "new_is_locked": True,
            "previous_status": previous_status,
            "new_status": user.status,
        },
    )

    db.commit()
    db.refresh(user)

    user = get_user_or_404(
        db=db,
        user_id=user.id,
    )

    return build_user_response(user)


def unlock_user(
    db: Session,
    user_id: int,
    *,
    admin_user_id: int | None = None,
    ip_address: str | None = None,
) -> AdminUserResponse:
    user = get_user_or_404(
        db=db,
        user_id=user_id,
    )

    previous_status = user.status
    previous_is_locked = user.is_locked
    previous_failed_attempts = user.failed_login_attempts

    user.is_locked = False
    user.failed_login_attempts = 0
    user.status = (
        "active"
        if user.is_active
        else "inactive"
    )

    create_audit_log(
        db=db,
        user_id=admin_user_id,
        action="USER_UNLOCKED",
        resource="user",
        resource_id=user.id,
        ip_address=ip_address,
        details={
            "target_user_email": user.email,
            "previous_is_locked": previous_is_locked,
            "new_is_locked": False,
            "previous_failed_login_attempts": (
                previous_failed_attempts
            ),
            "new_failed_login_attempts": 0,
            "previous_status": previous_status,
            "new_status": user.status,
        },
    )

    db.commit()
    db.refresh(user)

    user = get_user_or_404(
        db=db,
        user_id=user.id,
    )

    return build_user_response(user)


def reset_user_password(
    db: Session,
    user_id: int,
    request: AdminPasswordReset,
    *,
    admin_user_id: int | None = None,
    ip_address: str | None = None,
) -> AdminUserResponse:
    user = get_user_or_404(
        db=db,
        user_id=user_id,
    )

    user.password_hash = hash_password(
        request.new_password
    )

    user.password_changed_at = datetime.now(
        timezone.utc
    )

    user.failed_login_attempts = 0

    create_audit_log(
        db=db,
        user_id=admin_user_id,
        action="USER_PASSWORD_RESET",
        resource="user",
        resource_id=user.id,
        ip_address=ip_address,
        details={
            "target_user_email": user.email,
            "force_logout_requested": request.force_logout,
        },
    )

    db.commit()
    db.refresh(user)

    user = get_user_or_404(
        db=db,
        user_id=user.id,
    )

    return build_user_response(user)


def soft_delete_user(
    db: Session,
    user_id: int,
    *,
    admin_user_id: int | None = None,
    ip_address: str | None = None,
) -> User:
    user = get_user_or_404(
        db=db,
        user_id=user_id,
    )

    previous_values = {
        "is_deleted": user.is_deleted,
        "is_active": user.is_active,
        "is_locked": user.is_locked,
        "status": user.status,
    }

    user.is_deleted = True
    user.is_active = False
    user.is_locked = True
    user.status = "deleted"
    user.deleted_at = datetime.now(
        timezone.utc
    )

    create_audit_log(
        db=db,
        user_id=admin_user_id,
        action="USER_SOFT_DELETED",
        resource="user",
        resource_id=user.id,
        ip_address=ip_address,
        details={
            "target_user_email": user.email,
            "target_user_name": user.name,
            "previous_values": previous_values,
            "new_values": {
                "is_deleted": user.is_deleted,
                "is_active": user.is_active,
                "is_locked": user.is_locked,
                "status": user.status,
            },
        },
    )

    db.commit()
    db.refresh(user)

    return user
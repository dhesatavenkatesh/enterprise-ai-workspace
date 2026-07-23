from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.admin.audit.logger import create_audit_log
from app.admin.roles.schemas import (
    AdminPermissionListResponse,
    AdminPermissionResponse,
    AdminRoleCreate,
    AdminRoleListItem,
    AdminRoleListResponse,
    AdminRoleResponse,
    AdminRoleUpdate,
)
from app.models.permission import Permission
from app.models.role import Role
from app.models.role_permission import RolePermission
from app.models.user import User


def get_role_or_404(
    db: Session,
    role_id: int,
) -> Role:
    statement = (
        select(Role)
        .options(
            selectinload(
                Role.role_permissions
            ).selectinload(
                RolePermission.permission
            )
        )
        .where(Role.id == role_id)
    )

    role = db.scalar(statement)

    if role is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} was not found",
        )

    return role


def get_role_by_name(
    db: Session,
    name: str,
) -> Role | None:
    return db.scalar(
        select(Role).where(
            func.lower(Role.name)
            == name.strip().lower()
        )
    )


def get_role_user_count(
    db: Session,
    role_id: int,
) -> int:
    return (
        db.scalar(
            select(
                func.count(User.id)
            ).where(
                User.role_id == role_id,
                User.is_deleted.is_(False),
            )
        )
        or 0
    )


def get_role_permission_ids(
    role: Role,
) -> list[int]:
    return [
        role_permission.permission_id
        for role_permission in role.role_permissions
    ]


def build_permission_response(
    permission: Permission,
) -> AdminPermissionResponse:
    return AdminPermissionResponse(
        id=permission.id,
        permission_name=permission.permission_name,
        module=permission.module,
        description=permission.description,
        created_at=permission.created_at,
    )


def build_role_response(
    db: Session,
    role: Role,
) -> AdminRoleResponse:
    permissions = []

    for role_permission in role.role_permissions:
        permission = role_permission.permission

        if permission is None:
            continue

        permissions.append(
            build_permission_response(permission)
        )

    permissions.sort(
        key=lambda item: (
            item.module.lower(),
            item.permission_name.lower(),
        )
    )

    return AdminRoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
        permissions=permissions,
        user_count=get_role_user_count(
            db=db,
            role_id=role.id,
        ),
        created_at=role.created_at,
        updated_at=role.updated_at,
    )


def list_permissions(
    db: Session,
) -> AdminPermissionListResponse:
    permissions = db.scalars(
        select(Permission).order_by(
            Permission.module.asc(),
            Permission.permission_name.asc(),
        )
    ).all()

    items = [
        build_permission_response(permission)
        for permission in permissions
    ]

    return AdminPermissionListResponse(
        items=items,
        total=len(items),
    )


def validate_permission_ids(
    db: Session,
    permission_ids: list[int],
) -> list[int]:
    unique_ids = list(
        dict.fromkeys(permission_ids)
    )

    if not unique_ids:
        return []

    existing_ids = set(
        db.scalars(
            select(Permission.id).where(
                Permission.id.in_(unique_ids)
            )
        ).all()
    )

    missing_ids = [
        permission_id
        for permission_id in unique_ids
        if permission_id not in existing_ids
    ]

    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": (
                    "One or more permissions were not found"
                ),
                "missing_permission_ids": missing_ids,
            },
        )

    return unique_ids


def replace_role_permissions(
    db: Session,
    role_id: int,
    permission_ids: list[int],
) -> None:
    validated_ids = validate_permission_ids(
        db=db,
        permission_ids=permission_ids,
    )

    db.execute(
        delete(RolePermission).where(
            RolePermission.role_id == role_id
        )
    )

    for permission_id in validated_ids:
        db.add(
            RolePermission(
                role_id=role_id,
                permission_id=permission_id,
            )
        )

    db.flush()


def list_roles(
    db: Session,
) -> AdminRoleListResponse:
    roles = db.scalars(
        select(Role)
        .options(
            selectinload(
                Role.role_permissions
            )
        )
        .order_by(
            Role.name.asc()
        )
    ).unique().all()

    items = []

    for role in roles:
        items.append(
            AdminRoleListItem(
                id=role.id,
                name=role.name,
                description=role.description,
                permission_count=len(
                    role.role_permissions
                ),
                user_count=get_role_user_count(
                    db=db,
                    role_id=role.id,
                ),
                created_at=role.created_at,
                updated_at=role.updated_at,
            )
        )

    return AdminRoleListResponse(
        items=items,
        total=len(items),
    )


def get_role(
    db: Session,
    role_id: int,
) -> AdminRoleResponse:
    role = get_role_or_404(
        db=db,
        role_id=role_id,
    )

    return build_role_response(
        db=db,
        role=role,
    )


def create_role(
    db: Session,
    request: AdminRoleCreate,
    *,
    admin_user_id: int | None = None,
    ip_address: str | None = None,
) -> AdminRoleResponse:
    existing_role = get_role_by_name(
        db=db,
        name=request.name,
    )

    if existing_role is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A role with this name already exists",
        )

    validated_permission_ids = validate_permission_ids(
        db=db,
        permission_ids=request.permission_ids,
    )

    role = Role(
        name=request.name,
        description=request.description,
    )

    try:
        db.add(role)
        db.flush()

        replace_role_permissions(
            db=db,
            role_id=role.id,
            permission_ids=validated_permission_ids,
        )

        create_audit_log(
            db=db,
            user_id=admin_user_id,
            action="ROLE_CREATED",
            resource="role",
            resource_id=role.id,
            ip_address=ip_address,
            details={
                "role_name": role.name,
                "description": role.description,
                "permission_ids": (
                    validated_permission_ids
                ),
            },
        )

        db.commit()

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A role with this name already exists",
        ) from exc

    role = get_role_or_404(
        db=db,
        role_id=role.id,
    )

    return build_role_response(
        db=db,
        role=role,
    )


def update_role(
    db: Session,
    role_id: int,
    request: AdminRoleUpdate,
    *,
    admin_user_id: int | None = None,
    ip_address: str | None = None,
) -> AdminRoleResponse:
    role = get_role_or_404(
        db=db,
        role_id=role_id,
    )

    update_data = request.model_dump(
        exclude_unset=True,
    )

    previous_values: dict[str, Any] = {
        "name": role.name,
        "description": role.description,
        "permission_ids": get_role_permission_ids(role),
    }

    if "name" in update_data:
        duplicate_role = db.scalar(
            select(Role).where(
                func.lower(Role.name)
                == update_data["name"].lower(),
                Role.id != role.id,
            )
        )

        if duplicate_role is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Another role already uses this name",
            )

        role.name = update_data["name"]

    if "description" in update_data:
        role.description = update_data["description"]

    if "permission_ids" in update_data:
        replace_role_permissions(
            db=db,
            role_id=role.id,
            permission_ids=(
                update_data["permission_ids"] or []
            ),
        )

    try:
        db.flush()

        create_audit_log(
            db=db,
            user_id=admin_user_id,
            action="ROLE_UPDATED",
            resource="role",
            resource_id=role.id,
            ip_address=ip_address,
            details={
                "previous_values": previous_values,
                "new_values": update_data,
            },
        )

        db.commit()

    except IntegrityError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Unable to update role because "
                "the supplied data conflicts"
            ),
        ) from exc

    role = get_role_or_404(
        db=db,
        role_id=role.id,
    )

    return build_role_response(
        db=db,
        role=role,
    )


def update_role_permissions(
    db: Session,
    role_id: int,
    permission_ids: list[int],
    *,
    admin_user_id: int | None = None,
    ip_address: str | None = None,
) -> AdminRoleResponse:
    role = get_role_or_404(
        db=db,
        role_id=role_id,
    )

    previous_permission_ids = (
        get_role_permission_ids(role)
    )

    validated_permission_ids = validate_permission_ids(
        db=db,
        permission_ids=permission_ids,
    )

    replace_role_permissions(
        db=db,
        role_id=role.id,
        permission_ids=validated_permission_ids,
    )

    create_audit_log(
        db=db,
        user_id=admin_user_id,
        action="ROLE_PERMISSIONS_UPDATED",
        resource="role",
        resource_id=role.id,
        ip_address=ip_address,
        details={
            "role_name": role.name,
            "previous_permission_ids": (
                previous_permission_ids
            ),
            "new_permission_ids": (
                validated_permission_ids
            ),
        },
    )

    db.commit()

    role = get_role_or_404(
        db=db,
        role_id=role.id,
    )

    return build_role_response(
        db=db,
        role=role,
    )


def delete_role(
    db: Session,
    role_id: int,
    *,
    admin_user_id: int | None = None,
    ip_address: str | None = None,
) -> None:
    role = get_role_or_404(
        db=db,
        role_id=role_id,
    )

    assigned_user_count = get_role_user_count(
        db=db,
        role_id=role.id,
    )

    if assigned_user_count > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Cannot delete this role because it is "
                f"assigned to {assigned_user_count} user(s)"
            ),
        )

    role_details = {
        "role_name": role.name,
        "description": role.description,
        "permission_ids": get_role_permission_ids(role),
    }

    create_audit_log(
        db=db,
        user_id=admin_user_id,
        action="ROLE_DELETED",
        resource="role",
        resource_id=role.id,
        ip_address=ip_address,
        details=role_details,
    )

    db.execute(
        delete(RolePermission).where(
            RolePermission.role_id == role.id
        )
    )

    db.delete(role)
    db.commit()
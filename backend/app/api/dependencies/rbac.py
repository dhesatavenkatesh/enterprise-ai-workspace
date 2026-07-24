from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import Depends, HTTPException, status

from app.api.dependencies.auth import get_current_user
from app.models.user import User


def normalize_role(role: Any) -> str:
    """
    Convert a role object, enum, string or model into a lowercase role name.
    """

    if role is None:
        return ""

    if isinstance(role, str):
        return role.strip().lower()

    role_name = getattr(role, "name", None)

    if role_name:
        return str(role_name).strip().lower()

    role_value = getattr(role, "value", None)

    if role_value:
        return str(role_value).strip().lower()

    return str(role).strip().lower()


def get_user_roles(user: User) -> set[str]:
    """
    Return all roles assigned to the authenticated user.

    Supports:
    - user.role
    - user.roles
    - role.name
    - role.value
    """

    result: set[str] = set()

    direct_role = getattr(user, "role", None)

    if direct_role is not None:
        normalized = normalize_role(direct_role)

        if normalized:
            result.add(normalized)

    roles = getattr(user, "roles", None)

    if roles:
        for role in roles:
            normalized = normalize_role(role)

            if normalized:
                result.add(normalized)

    return result


def get_user_role(user: User) -> str:
    """
    Return one role name for compatibility with older code.
    """

    roles = get_user_roles(user)

    if not roles:
        return ""

    priority = [
        "admin",
        "hr",
        "manager",
        "employee",
    ]

    for role in priority:
        if role in roles:
            return role

    return next(iter(roles))


def normalize_permission(permission: Any) -> str:
    """
    Convert a permission model, enum or string into a permission name.
    """

    if permission is None:
        return ""

    if isinstance(permission, str):
        return permission.strip().lower()

    permission_name = getattr(permission, "name", None)

    if permission_name:
        return str(permission_name).strip().lower()

    permission_code = getattr(permission, "code", None)

    if permission_code:
        return str(permission_code).strip().lower()

    permission_value = getattr(permission, "value", None)

    if permission_value:
        return str(permission_value).strip().lower()

    return str(permission).strip().lower()


def get_user_permissions(user: User) -> set[str]:
    """
    Return all permissions assigned directly or through roles.

    Supports common relationships such as:
    - user.permissions
    - user.roles[].permissions
    """

    result: set[str] = set()

    direct_permissions = getattr(user, "permissions", None)

    if direct_permissions:
        for permission in direct_permissions:
            normalized = normalize_permission(permission)

            if normalized:
                result.add(normalized)

    roles = getattr(user, "roles", None)

    if roles:
        for role in roles:
            role_permissions = getattr(role, "permissions", None)

            if not role_permissions:
                continue

            for permission in role_permissions:
                normalized = normalize_permission(permission)

                if normalized:
                    result.add(normalized)

    direct_role = getattr(user, "role", None)
    role_permissions = getattr(direct_role, "permissions", None)

    if role_permissions:
        for permission in role_permissions:
            normalized = normalize_permission(permission)

            if normalized:
                result.add(normalized)

    return result


def require_roles(
    *allowed_roles: str,
) -> Callable:
    """
    Allow only users having at least one of the supplied roles.

    Example:

        current_user: User = Depends(
            require_roles("admin", "manager")
        )
    """

    normalized_allowed_roles = {
        role.strip().lower() for role in allowed_roles if role and role.strip()
    }

    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        current_roles = get_user_roles(current_user)

        if not current_roles.intersection(normalized_allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=("You do not have permission to perform this action."),
            )

        return current_user

    return role_checker


def require_permission(
    permission_name: str,
) -> Callable:
    """
    Allow users who have the requested permission.

    Administrators are allowed automatically.

    Example:

        current_user: User = Depends(
            require_permission("document:upload")
        )
    """

    normalized_required_permission = permission_name.strip().lower()

    def permission_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        current_roles = get_user_roles(current_user)

        if "admin" in current_roles:
            return current_user

        current_permissions = get_user_permissions(current_user)

        if normalized_required_permission not in current_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"You do not have the required permission: {normalized_required_permission}"
                ),
            )

        return current_user

    return permission_checker


def require_any_permission(
    *permission_names: str,
) -> Callable:
    """
    Allow users who have at least one required permission.

    Administrators are allowed automatically.
    """

    normalized_permissions = {
        permission.strip().lower()
        for permission in permission_names
        if permission and permission.strip()
    }

    def permission_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        current_roles = get_user_roles(current_user)

        if "admin" in current_roles:
            return current_user

        current_permissions = get_user_permissions(current_user)

        if not current_permissions.intersection(normalized_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=("You do not have any of the required permissions."),
            )

        return current_user

    return permission_checker


def require_all_permissions(
    *permission_names: str,
) -> Callable:
    """
    Allow users only when all requested permissions are assigned.

    Administrators are allowed automatically.
    """

    normalized_permissions = {
        permission.strip().lower()
        for permission in permission_names
        if permission and permission.strip()
    }

    def permission_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        current_roles = get_user_roles(current_user)

        if "admin" in current_roles:
            return current_user

        current_permissions = get_user_permissions(current_user)

        missing_permissions = normalized_permissions - current_permissions

        if missing_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": ("You do not have all required permissions."),
                    "missing_permissions": sorted(missing_permissions),
                },
            )

        return current_user

    return permission_checker


def require_admin(
    current_user: User = Depends(require_roles("admin")),
) -> User:
    """
    Allow administrators only.
    """

    return current_user


def require_admin_or_manager(
    current_user: User = Depends(require_roles("admin", "manager")),
) -> User:
    """
    Allow administrators and managers.
    """

    return current_user


def require_admin_manager_or_hr(
    current_user: User = Depends(
        require_roles(
            "admin",
            "manager",
            "hr",
        )
    ),
) -> User:
    """
    Allow administrators, managers and HR users.
    """

    return current_user


def is_admin(user: User) -> bool:
    return "admin" in get_user_roles(user)


def is_manager(user: User) -> bool:
    return "manager" in get_user_roles(user)


def is_hr(user: User) -> bool:
    return "hr" in get_user_roles(user)


def is_employee(user: User) -> bool:
    return "employee" in get_user_roles(user)

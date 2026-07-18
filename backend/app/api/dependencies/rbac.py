from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies.auth import get_current_user
from app.database.session import get_db
from app.models.permission import Permission
from app.models.role_permission import RolePermission
from app.models.user import User
from app.core.exceptions import PermissionDeniedError

def permission_denied() -> PermissionDeniedError:
    return PermissionDeniedError(
        "Permission Denied"
    )


def require_roles(
    *allowed_roles: str,
) -> Callable:
    def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        user_role = current_user.role.name.lower()

        normalized_roles = {
            role.lower()
            for role in allowed_roles
        }

        if user_role == "admin":
            return current_user

        if user_role not in normalized_roles:
            raise permission_denied()

        return current_user

    return role_checker


def require_permission(
    permission_name: str,
) -> Callable:
    def permission_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        if current_user.role.name.lower() == "admin":
            return current_user

        statement = (
            select(Permission)
            .join(
                RolePermission,
                RolePermission.permission_id
                == Permission.id,
            )
            .where(
                RolePermission.role_id
                == current_user.role_id,
                Permission.permission_name
                == permission_name,
            )
        )

        permission = db.scalar(statement)

        if permission is None:
            raise permission_denied()

        return current_user

    return permission_checker
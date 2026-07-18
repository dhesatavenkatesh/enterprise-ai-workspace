from fastapi import APIRouter, Depends

from app.api.dependencies.rbac import require_roles
from app.models.user import User
from app.api.dependencies.rbac import (
    require_permission,
    require_roles,
)

router = APIRouter(
    prefix="/api",
    tags=["RBAC"],
)


@router.get("/admin/test")
def admin_test(
    current_user: User = Depends(
        require_roles("Admin")
    ),
) -> dict:
    return {
        "message": "Admin access granted",
        "user": current_user.email,
        "role": current_user.role.name,
    }


@router.get("/hr/test")
def hr_test(
    current_user: User = Depends(
        require_roles("Admin", "HR")
    ),
) -> dict:
    return {
        "message": "HR access granted",
        "user": current_user.email,
        "role": current_user.role.name,
    }


@router.get("/employee/test")
def employee_test(
    current_user: User = Depends(
        require_roles(
            "Admin",
            "HR",
            "Manager",
            "Employee",
            "Support",
        )
    ),
) -> dict:
    return {
        "message": "Employee access granted",
        "user": current_user.email,
        "role": current_user.role.name,
    }


@router.get("/manager/test")
def manager_test(
    current_user: User = Depends(
        require_roles("Admin", "Manager")
    ),
) -> dict:
    return {
        "message": "Manager access granted",
        "user": current_user.email,
        "role": current_user.role.name,
    }


@router.get("/support/test")
def support_test(
    current_user: User = Depends(
        require_roles("Admin", "Support")
    ),
) -> dict:
    return {
        "message": "Support access granted",
        "user": current_user.email,
        "role": current_user.role.name,
    }
@router.get("/chat/test")
def chat_test(
    current_user: User = Depends(
        require_permission("chat.access")
    ),
) -> dict:
    return {
        "message": "AI Chat access granted",
        "user": current_user.email,
        "role": current_user.role.name,
    }
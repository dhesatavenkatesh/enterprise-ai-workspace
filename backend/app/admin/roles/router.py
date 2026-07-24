from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Request,
    status,
)
from sqlalchemy.orm import Session

from app.admin.audit.utils import get_client_ip
from app.admin.roles.schemas import (
    AdminPermissionListResponse,
    AdminRoleActionResponse,
    AdminRoleCreate,
    AdminRoleDeleteResponse,
    AdminRoleListResponse,
    AdminRolePermissionUpdate,
    AdminRoleResponse,
    AdminRoleUpdate,
)
from app.admin.roles.service import (
    create_role,
    delete_role,
    get_role,
    list_permissions,
    list_roles,
    update_role,
    update_role_permissions,
)
from app.api.dependencies.rbac import require_admin
from app.database.session import get_db
from app.models.user import User

router = APIRouter(
    prefix="/roles",
    tags=["Sprint 5 - Admin Roles"],
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
    "/permissions",
    response_model=AdminPermissionListResponse,
    summary="List available permissions",
    description=("Returns all available permissions that can be assigned to roles."),
)
def get_admin_permissions(
    db: DatabaseSession,
    current_user: AdminUser,
) -> AdminPermissionListResponse:
    return list_permissions(
        db=db,
    )


@router.get(
    "",
    response_model=AdminRoleListResponse,
    summary="List roles",
    description=("Returns all roles with their permission and assigned-user counts."),
)
def get_admin_roles(
    db: DatabaseSession,
    current_user: AdminUser,
) -> AdminRoleListResponse:
    return list_roles(
        db=db,
    )


@router.post(
    "",
    response_model=AdminRoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create role",
    description=("Creates a new role and optionally assigns permissions to it."),
)
def create_admin_role(
    payload: AdminRoleCreate,
    request: Request,
    db: DatabaseSession,
    current_user: AdminUser,
) -> AdminRoleResponse:
    return create_role(
        db=db,
        request=payload,
        admin_user_id=current_user.id,
        ip_address=get_client_ip(request),
    )


@router.get(
    "/{role_id}",
    response_model=AdminRoleResponse,
    summary="Get role details",
    description=("Returns one role with its assigned permissions and user count."),
)
def get_admin_role(
    role_id: int,
    db: DatabaseSession,
    current_user: AdminUser,
) -> AdminRoleResponse:
    return get_role(
        db=db,
        role_id=role_id,
    )


@router.put(
    "/{role_id}",
    response_model=AdminRoleResponse,
    summary="Update role",
    description=("Updates a role name, description, or permissions."),
)
def update_admin_role(
    role_id: int,
    payload: AdminRoleUpdate,
    request: Request,
    db: DatabaseSession,
    current_user: AdminUser,
) -> AdminRoleResponse:
    return update_role(
        db=db,
        role_id=role_id,
        request=payload,
        admin_user_id=current_user.id,
        ip_address=get_client_ip(request),
    )


@router.patch(
    "/{role_id}",
    response_model=AdminRoleResponse,
    summary="Partially update role",
    description=("Partially updates a role name, description, or permissions."),
)
def patch_admin_role(
    role_id: int,
    payload: AdminRoleUpdate,
    request: Request,
    db: DatabaseSession,
    current_user: AdminUser,
) -> AdminRoleResponse:
    return update_role(
        db=db,
        role_id=role_id,
        request=payload,
        admin_user_id=current_user.id,
        ip_address=get_client_ip(request),
    )


@router.put(
    "/{role_id}/permissions",
    response_model=AdminRoleActionResponse,
    summary="Replace role permissions",
    description=("Replaces all existing permissions assigned to the selected role."),
)
def replace_admin_role_permissions(
    role_id: int,
    payload: AdminRolePermissionUpdate,
    request: Request,
    db: DatabaseSession,
    current_user: AdminUser,
) -> AdminRoleActionResponse:
    role = update_role_permissions(
        db=db,
        role_id=role_id,
        permission_ids=payload.permission_ids,
        admin_user_id=current_user.id,
        ip_address=get_client_ip(request),
    )

    return AdminRoleActionResponse(
        message=("Role permissions updated successfully"),
        role=role,
    )


@router.delete(
    "/{role_id}",
    response_model=AdminRoleDeleteResponse,
    summary="Delete role",
    description=("Deletes a role when it is not assigned to any active user."),
)
def delete_admin_role(
    role_id: int,
    request: Request,
    db: DatabaseSession,
    current_user: AdminUser,
) -> AdminRoleDeleteResponse:
    delete_role(
        db=db,
        role_id=role_id,
        admin_user_id=current_user.id,
        ip_address=get_client_ip(request),
    )

    return AdminRoleDeleteResponse(
        message="Role deleted successfully",
        role_id=role_id,
    )

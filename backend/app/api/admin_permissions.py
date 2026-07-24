from __future__ import annotations

from math import ceil

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

router = APIRouter(
    prefix="/api/admin/permissions",
    tags=["Admin Permissions"],
)


class PermissionCreate(BaseModel):
    permission_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )
    module: str = Field(
        ...,
        min_length=2,
        max_length=100,
    )
    description: str | None = Field(
        default=None,
        max_length=500,
    )


class PermissionUpdate(BaseModel):
    permission_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    module: str | None = Field(
        default=None,
        min_length=2,
        max_length=100,
    )
    description: str | None = Field(
        default=None,
        max_length=500,
    )


class PermissionResponse(BaseModel):
    id: int
    permission_name: str
    module: str
    description: str | None = None
    created_at: str | None = None


class PermissionListResponse(BaseModel):
    items: list[PermissionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class RolePermissionUpdate(BaseModel):
    permission_ids: list[int]


# Temporary in-memory data.
# Replace this with PostgreSQL queries later.
_permissions: list[dict] = [
    {
        "id": 1,
        "permission_name": "USER_VIEW",
        "module": "users",
        "description": "View users",
        "created_at": None,
    },
    {
        "id": 2,
        "permission_name": "USER_CREATE",
        "module": "users",
        "description": "Create users",
        "created_at": None,
    },
    {
        "id": 3,
        "permission_name": "USER_UPDATE",
        "module": "users",
        "description": "Update users",
        "created_at": None,
    },
    {
        "id": 4,
        "permission_name": "USER_DELETE",
        "module": "users",
        "description": "Delete users",
        "created_at": None,
    },
    {
        "id": 5,
        "permission_name": "AUDIT_VIEW",
        "module": "audit",
        "description": "View audit logs",
        "created_at": None,
    },
]

_role_permissions: dict[int, list[int]] = {}


@router.get(
    "",
    response_model=PermissionListResponse,
)
async def list_permissions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=500),
    search: str | None = Query(default=None),
    module: str | None = Query(default=None),
) -> PermissionListResponse:
    filtered = _permissions.copy()

    if search:
        normalized_search = search.strip().lower()

        filtered = [
            permission
            for permission in filtered
            if normalized_search in permission["permission_name"].lower()
            or normalized_search in permission["module"].lower()
            or normalized_search in (permission["description"] or "").lower()
        ]

    if module:
        normalized_module = module.strip().lower()

        filtered = [
            permission
            for permission in filtered
            if permission["module"].lower() == normalized_module
        ]

    total = len(filtered)
    total_pages = max(
        1,
        ceil(total / page_size),
    )

    start = (page - 1) * page_size
    end = start + page_size

    items = filtered[start:end]

    return PermissionListResponse(
        items=[PermissionResponse(**item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post(
    "",
    response_model=PermissionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_permission(
    payload: PermissionCreate,
) -> PermissionResponse:
    permission_name = payload.permission_name.strip().upper()

    module = payload.module.strip().lower()

    duplicate = next(
        (
            permission
            for permission in _permissions
            if permission["permission_name"] == permission_name
        ),
        None,
    )

    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Permission already exists.",
        )

    next_id = (
        max(
            (permission["id"] for permission in _permissions),
            default=0,
        )
        + 1
    )

    permission = {
        "id": next_id,
        "permission_name": permission_name,
        "module": module,
        "description": (payload.description.strip() if payload.description else None),
        "created_at": None,
    }

    _permissions.append(permission)

    return PermissionResponse(**permission)


@router.get(
    "/{permission_id}",
    response_model=PermissionResponse,
)
async def get_permission(
    permission_id: int,
) -> PermissionResponse:
    permission = next(
        (permission for permission in _permissions if permission["id"] == permission_id),
        None,
    )

    if permission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found.",
        )

    return PermissionResponse(**permission)


@router.put(
    "/{permission_id}",
    response_model=PermissionResponse,
)
async def update_permission(
    permission_id: int,
    payload: PermissionUpdate,
) -> PermissionResponse:
    permission = next(
        (permission for permission in _permissions if permission["id"] == permission_id),
        None,
    )

    if permission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found.",
        )

    if payload.permission_name is not None:
        permission["permission_name"] = payload.permission_name.strip().upper()

    if payload.module is not None:
        permission["module"] = payload.module.strip().lower()

    if payload.description is not None:
        permission["description"] = payload.description.strip() or None

    return PermissionResponse(**permission)


@router.delete(
    "/{permission_id}",
)
async def delete_permission(
    permission_id: int,
) -> dict[str, int | str]:
    permission = next(
        (permission for permission in _permissions if permission["id"] == permission_id),
        None,
    )

    if permission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Permission not found.",
        )

    _permissions.remove(permission)

    for role_id, permission_ids in _role_permissions.items():
        _role_permissions[role_id] = [
            current_id for current_id in permission_ids if current_id != permission_id
        ]

    return {
        "message": "Permission deleted successfully.",
        "deleted_permission_id": permission_id,
    }


@router.put(
    "/roles/{role_id}",
)
async def update_role_permissions(
    role_id: int,
    payload: RolePermissionUpdate,
) -> dict[str, object]:
    existing_ids = {permission["id"] for permission in _permissions}

    invalid_ids = [
        permission_id
        for permission_id in payload.permission_ids
        if permission_id not in existing_ids
    ]

    if invalid_ids:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Invalid permission IDs.",
                "invalid_permission_ids": invalid_ids,
            },
        )

    _role_permissions[role_id] = list(dict.fromkeys(payload.permission_ids))

    return {
        "message": "Role permissions updated successfully.",
        "role_id": role_id,
        "permission_ids": _role_permissions[role_id],
    }

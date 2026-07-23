from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.admin.dashboard.schemas import (
    AdminDashboardResponse,
)
from app.admin.dashboard.service import (
    get_dashboard_summary,
)
from app.api.dependencies.rbac import require_admin
from app.database.session import get_db
from app.models.user import User


router = APIRouter(
    prefix="/dashboard",
    tags=["Sprint 5 - Admin Dashboard"],
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
    response_model=AdminDashboardResponse,
    summary="Get admin dashboard summary",
)
def get_admin_dashboard(
    db: DatabaseSession,
    current_user: AdminUser,
) -> AdminDashboardResponse:
    return get_dashboard_summary(
        db=db,
    )
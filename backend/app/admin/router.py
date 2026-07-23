from fastapi import APIRouter

from app.admin.audit.router import router as audit_router
from app.admin.dashboard.router import router as dashboard_router
from app.admin.roles.router import router as roles_router
from app.admin.users.router import router as users_router


router = APIRouter(
    prefix="/api/admin",
)


router.include_router(users_router)
router.include_router(roles_router)
router.include_router(dashboard_router)
router.include_router(audit_router)
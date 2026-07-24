from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from app.admin.audit.schemas import (
    AdminAuditLogListResponse,
    AdminAuditLogResponse,
)
from app.admin.audit.service import (
    get_audit_log_by_id,
    list_audit_logs,
)
from app.database.session import get_db

router = APIRouter(
    prefix="/audit-logs",
    tags=["Sprint 5 - Audit Logs"],
)


@router.get(
    "",
    response_model=AdminAuditLogListResponse,
    summary="List audit logs",
)
def get_all_audit_logs(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    action: str | None = Query(
        default=None,
    ),
    resource: str | None = Query(
        default=None,
    ),
    user_id: int | None = Query(
        default=None,
        ge=1,
    ),
    search: str | None = Query(
        default=None,
    ),
    db: Session = Depends(get_db),
) -> AdminAuditLogListResponse:
    return list_audit_logs(
        db=db,
        page=page,
        page_size=page_size,
        action=action,
        resource=resource,
        user_id=user_id,
        search=search,
    )


@router.get(
    "/{audit_log_id}",
    response_model=AdminAuditLogResponse,
    summary="Get audit log by ID",
)
def get_single_audit_log(
    audit_log_id: int,
    db: Session = Depends(get_db),
) -> AdminAuditLogResponse:
    audit_log = get_audit_log_by_id(
        db=db,
        audit_log_id=audit_log_id,
    )

    if audit_log is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found",
        )

    return AdminAuditLogResponse.model_validate(audit_log)

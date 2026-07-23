import math

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.admin.audit.schemas import (
    AdminAuditLogListResponse,
    AdminAuditLogResponse,
)
from app.models.audit_log import AuditLog


def list_audit_logs(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    action: str | None = None,
    resource: str | None = None,
    user_id: int | None = None,
    search: str | None = None,
) -> AdminAuditLogListResponse:
    filters = []

    if action:
        filters.append(
            func.lower(AuditLog.action)
            == action.strip().lower()
        )

    if resource:
        filters.append(
            func.lower(AuditLog.resource)
            == resource.strip().lower()
        )

    if user_id is not None:
        filters.append(
            AuditLog.user_id == user_id
        )

    if search and search.strip():
        search_value = f"%{search.strip()}%"

        filters.append(
            or_(
                AuditLog.action.ilike(search_value),
                AuditLog.resource.ilike(search_value),
                AuditLog.resource_id.ilike(search_value),
                AuditLog.details.ilike(search_value),
                AuditLog.ip_address.ilike(search_value),
            )
        )

    count_query = select(
        func.count(AuditLog.id)
    )

    if filters:
        count_query = count_query.where(*filters)

    total = db.scalar(count_query) or 0

    query = select(AuditLog)

    if filters:
        query = query.where(*filters)

    query = (
        query
        .order_by(
            AuditLog.created_at.desc(),
            AuditLog.id.desc(),
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    records = db.scalars(query).all()

    items = [
        AdminAuditLogResponse.model_validate(record)
        for record in records
    ]

    total_pages = (
        math.ceil(total / page_size)
        if total > 0
        else 0
    )

    return AdminAuditLogListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def get_audit_log_by_id(
    db: Session,
    audit_log_id: int,
) -> AuditLog | None:
    return db.get(
        AuditLog,
        audit_log_id,
    )
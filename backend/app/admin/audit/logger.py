import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


def create_audit_log(
    db: Session,
    *,
    action: str,
    resource: str | None = None,
    user_id: int | None = None,
    resource_id: str | int | None = None,
    ip_address: str | None = None,
    details: dict[str, Any] | str | None = None,
) -> AuditLog:
    """
    Create an audit-log record inside the current database transaction.

    This function calls db.flush(), but it does not call db.commit().
    The calling service should commit the complete transaction.
    """

    if isinstance(details, dict):
        details_value = json.dumps(
            details,
            default=str,
            ensure_ascii=False,
        )
    else:
        details_value = details

    audit_log = AuditLog(
        user_id=user_id,
        action=action.strip().upper(),
        resource=resource.strip().lower() if resource else None,
        resource_id=(
            str(resource_id)
            if resource_id is not None
            else None
        ),
        ip_address=ip_address,
        details=details_value,
    )

    db.add(audit_log)
    db.flush()

    return audit_log
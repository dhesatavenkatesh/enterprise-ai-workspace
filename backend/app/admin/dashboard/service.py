from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.admin.dashboard.schemas import (
    AdminDashboardAuditStats,
    AdminDashboardRecentAuditItem,
    AdminDashboardResponse,
    AdminDashboardRoleStats,
    AdminDashboardUserStats,
)
from app.models.audit_log import AuditLog
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User


def get_user_statistics(
    db: Session,
) -> AdminDashboardUserStats:
    total_users = (
        db.scalar(
            select(
                func.count(User.id)
            )
        )
        or 0
    )

    active_users = (
        db.scalar(
            select(
                func.count(User.id)
            ).where(
                User.is_active.is_(True),
                User.is_deleted.is_(False),
            )
        )
        or 0
    )

    inactive_users = (
        db.scalar(
            select(
                func.count(User.id)
            ).where(
                User.is_active.is_(False),
                User.is_deleted.is_(False),
            )
        )
        or 0
    )

    locked_users = (
        db.scalar(
            select(
                func.count(User.id)
            ).where(
                User.is_locked.is_(True),
                User.is_deleted.is_(False),
            )
        )
        or 0
    )

    deleted_users = (
        db.scalar(
            select(
                func.count(User.id)
            ).where(
                User.is_deleted.is_(True)
            )
        )
        or 0
    )

    return AdminDashboardUserStats(
        total=total_users,
        active=active_users,
        inactive=inactive_users,
        locked=locked_users,
        deleted=deleted_users,
    )


def get_role_statistics(
    db: Session,
) -> AdminDashboardRoleStats:
    total_roles = (
        db.scalar(
            select(
                func.count(Role.id)
            )
        )
        or 0
    )

    total_permissions = (
        db.scalar(
            select(
                func.count(Permission.id)
            )
        )
        or 0
    )

    return AdminDashboardRoleStats(
        total_roles=total_roles,
        total_permissions=total_permissions,
    )


def get_audit_statistics(
    db: Session,
) -> AdminDashboardAuditStats:
    total_logs = (
        db.scalar(
            select(
                func.count(AuditLog.id)
            )
        )
        or 0
    )

    today = datetime.now(
        timezone.utc
    ).date()

    logs_today = (
        db.scalar(
            select(
                func.count(AuditLog.id)
            ).where(
                func.date(
                    AuditLog.created_at
                )
                == today
            )
        )
        or 0
    )

    return AdminDashboardAuditStats(
        total_logs=total_logs,
        logs_today=logs_today,
    )


def get_recent_audit_logs(
    db: Session,
    limit: int = 10,
) -> list[AdminDashboardRecentAuditItem]:
    logs = db.scalars(
        select(AuditLog)
        .order_by(
            AuditLog.created_at.desc(),
            AuditLog.id.desc(),
        )
        .limit(limit)
    ).all()

    return [
        AdminDashboardRecentAuditItem(
            id=log.id,
            user_id=log.user_id,
            action=log.action,
            resource=log.resource,
            resource_id=log.resource_id,
            ip_address=log.ip_address,
            created_at=log.created_at,
        )
        for log in logs
    ]


def get_dashboard_summary(
    db: Session,
) -> AdminDashboardResponse:
    return AdminDashboardResponse(
        users=get_user_statistics(
            db=db,
        ),
        roles=get_role_statistics(
            db=db,
        ),
        audit=get_audit_statistics(
            db=db,
        ),
        recent_audit_logs=get_recent_audit_logs(
            db=db,
            limit=10,
        ),
        generated_at=datetime.now(
            timezone.utc
        ),
    )
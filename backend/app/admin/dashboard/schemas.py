from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class AdminDashboardUserStats(BaseModel):
    total: int = 0
    active: int = 0
    inactive: int = 0
    locked: int = 0
    deleted: int = 0


class AdminDashboardRoleStats(BaseModel):
    total_roles: int = 0
    total_permissions: int = 0


class AdminDashboardAuditStats(BaseModel):
    total_logs: int = 0
    logs_today: int = 0


class AdminDashboardRecentAuditItem(BaseModel):
    id: int
    user_id: int | None = None
    action: str
    resource: str
    resource_id: int | None = None
    ip_address: str | None = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class AdminDashboardResponse(BaseModel):
    users: AdminDashboardUserStats
    roles: AdminDashboardRoleStats
    audit: AdminDashboardAuditStats

    recent_audit_logs: list[
        AdminDashboardRecentAuditItem
    ] = Field(
        default_factory=list,
    )

    generated_at: datetime
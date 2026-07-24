from __future__ import annotations

from datetime import UTC, datetime

from app.approvals.schemas import (
    ApprovalCreate,
    ApprovalDecision,
    ApprovalRequest,
    ApprovalStatus,
)
from app.approvals.store import ApprovalStore, approval_store


def utc_now() -> datetime:
    return datetime.now(UTC)


class ApprovalService:
    def __init__(self, store: ApprovalStore | None = None) -> None:
        self.store = store or approval_store

    def create(self, payload: ApprovalCreate) -> ApprovalRequest:
        return self.store.create(ApprovalRequest(**payload.model_dump()))

    def get(self, approval_id: str) -> ApprovalRequest:
        return self.store.get(approval_id)

    def list(
        self,
        *,
        status: ApprovalStatus | None = None,
        requested_by: int | str | None = None,
    ) -> list[ApprovalRequest]:
        return self.store.list(status=status, requested_by=requested_by)

    def approve(
        self,
        approval_id: str,
        decision: ApprovalDecision,
        decided_by: int | str,
    ) -> ApprovalRequest:
        return self._decide(
            approval_id,
            ApprovalStatus.APPROVED,
            decision,
            decided_by,
        )

    def reject(
        self,
        approval_id: str,
        decision: ApprovalDecision,
        decided_by: int | str,
    ) -> ApprovalRequest:
        return self._decide(
            approval_id,
            ApprovalStatus.REJECTED,
            decision,
            decided_by,
        )

    def _decide(
        self,
        approval_id: str,
        status: ApprovalStatus,
        decision: ApprovalDecision,
        decided_by: int | str,
    ) -> ApprovalRequest:
        item = self.store.get(approval_id)
        if item.status != ApprovalStatus.PENDING:
            raise ValueError(f"Approval request is already '{item.status.value}'.")
        item.status = status
        item.decided_by = decided_by
        item.decision_comment = decision.comment
        item.decided_at = utc_now()
        return self.store.save(item)

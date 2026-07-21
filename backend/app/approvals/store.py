from __future__ import annotations

from threading import RLock

from app.approvals.schemas import ApprovalRequest, ApprovalStatus


class ApprovalStore:
    def __init__(self) -> None:
        self._items: dict[str, ApprovalRequest] = {}
        self._lock = RLock()

    def create(self, item: ApprovalRequest) -> ApprovalRequest:
        with self._lock:
            self._items[item.id] = item
        return item

    def get(self, approval_id: str) -> ApprovalRequest:
        with self._lock:
            item = self._items.get(approval_id)
        if item is None:
            raise KeyError(f"Approval request '{approval_id}' was not found.")
        return item

    def save(self, item: ApprovalRequest) -> ApprovalRequest:
        with self._lock:
            self._items[item.id] = item
        return item

    def list(
        self,
        *,
        status: ApprovalStatus | None = None,
        requested_by: int | str | None = None,
    ) -> list[ApprovalRequest]:
        with self._lock:
            items = list(self._items.values())
        if status is not None:
            items = [item for item in items if item.status == status]
        if requested_by is not None:
            items = [
                item for item in items
                if str(item.requested_by) == str(requested_by)
            ]
        return sorted(items, key=lambda item: item.created_at, reverse=True)


approval_store = ApprovalStore()

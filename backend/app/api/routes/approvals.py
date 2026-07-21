from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies.auth import get_current_user
from app.approvals.schemas import (
    ApprovalDecision,
    ApprovalListResponse,
    ApprovalRequest,
    ApprovalStatus,
)
from app.approvals.service import ApprovalService
from app.models.user import User


router = APIRouter(prefix="/api/approvals", tags=["Human Approval"])


def get_approval_service() -> ApprovalService:
    return ApprovalService()


@router.get("", response_model=ApprovalListResponse)
def list_approvals(
    approval_status: ApprovalStatus | None = Query(default=None, alias="status"),
    mine_only: bool = False,
    current_user: User = Depends(get_current_user),
    service: ApprovalService = Depends(get_approval_service),
) -> ApprovalListResponse:
    items = service.list(
        status=approval_status,
        requested_by=current_user.id if mine_only else None,
    )
    return ApprovalListResponse(total=len(items), items=items)


@router.get("/{approval_id}", response_model=ApprovalRequest)
def get_approval(
    approval_id: str,
    current_user: User = Depends(get_current_user),
    service: ApprovalService = Depends(get_approval_service),
) -> ApprovalRequest:
    del current_user
    try:
        return service.get(approval_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/{approval_id}/approve", response_model=ApprovalRequest)
def approve_request(
    approval_id: str,
    payload: ApprovalDecision,
    current_user: User = Depends(get_current_user),
    service: ApprovalService = Depends(get_approval_service),
) -> ApprovalRequest:
    try:
        return service.approve(approval_id, payload, current_user.id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{approval_id}/reject", response_model=ApprovalRequest)
def reject_request(
    approval_id: str,
    payload: ApprovalDecision,
    current_user: User = Depends(get_current_user),
    service: ApprovalService = Depends(get_approval_service),
) -> ApprovalRequest:
    try:
        return service.reject(approval_id, payload, current_user.id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

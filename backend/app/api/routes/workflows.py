from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.workflows.engine import WorkflowEngine
from app.workflows.schemas import (
    WorkflowCreate,
    WorkflowDefinition,
    WorkflowRunRequest,
    WorkflowRunResult,
)
from app.workflows.service import WorkflowService
from app.workflows.store import workflow_store

router = APIRouter(prefix="/api/workflows", tags=["Workflow Engine"])


def get_workflow_service() -> WorkflowService:
    return WorkflowService(workflow_store)


def get_workflow_engine() -> WorkflowEngine:
    return WorkflowEngine(workflow_store)


@router.post("", response_model=WorkflowDefinition, status_code=status.HTTP_201_CREATED)
def create_workflow(
    payload: WorkflowCreate,
    current_user: User = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service),
) -> WorkflowDefinition:
    return service.create(payload, current_user.id)


@router.get("", response_model=list[WorkflowDefinition])
def list_workflows(
    current_user: User = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service),
) -> list[WorkflowDefinition]:
    return service.list(current_user.id)


@router.get("/{workflow_id}", response_model=WorkflowDefinition)
def get_workflow(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service),
) -> WorkflowDefinition:
    try:
        return service.get(workflow_id, current_user.id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


@router.post("/{workflow_id}/run", response_model=WorkflowRunResult)
async def run_workflow(
    workflow_id: str,
    payload: WorkflowRunRequest,
    current_user: User = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service),
    engine: WorkflowEngine = Depends(get_workflow_engine),
) -> WorkflowRunResult:
    try:
        workflow = service.get(workflow_id, current_user.id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return await engine.run(workflow, payload, user_id=current_user.id)


@router.post("/runs/{run_id}/resume", response_model=WorkflowRunResult)
async def resume_workflow_run(
    run_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service),
    engine: WorkflowEngine = Depends(get_workflow_engine),
) -> WorkflowRunResult:
    try:
        run = workflow_store.get_run(run_id)
        workflow = service.get(run.workflow_id, current_user.id)
        return await engine.resume(workflow, run, user_id=current_user.id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.get("/{workflow_id}/runs", response_model=list[WorkflowRunResult])
def list_workflow_runs(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    service: WorkflowService = Depends(get_workflow_service),
) -> list[WorkflowRunResult]:
    try:
        service.get(workflow_id, current_user.id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return workflow_store.list_runs(workflow_id)


@router.get("/runs/{run_id}/status", response_model=WorkflowRunResult)
def get_workflow_run(
    run_id: str,
    current_user: User = Depends(get_current_user),
) -> WorkflowRunResult:
    del current_user
    try:
        return workflow_store.get_run(run_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.agents.bootstrap import register_default_agents
from app.api.dependencies.auth import get_current_user
from app.models.user import User
from app.orchestrator.schemas import OrchestratorRequest, OrchestratorResponse
from app.orchestrator.service import AgentOrchestrator

router = APIRouter(
    prefix="/api/agents",
    tags=["Multi-Agent Orchestrator"],
)


def get_orchestrator() -> AgentOrchestrator:
    registry = register_default_agents()
    return AgentOrchestrator(registry=registry)


@router.get("")
def list_agents(
    current_user: User = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
) -> dict:
    del current_user
    return {"agents": orchestrator.registry.list()}


@router.post("/route", response_model=OrchestratorResponse)
async def route_agent_request(
    payload: OrchestratorRequest,
    current_user: User = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
) -> OrchestratorResponse:
    return await orchestrator.auto_route(payload, user_id=current_user.id)


@router.post("/execute", response_model=OrchestratorResponse)
async def execute_single_agent(
    payload: OrchestratorRequest,
    current_user: User = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
) -> OrchestratorResponse:
    try:
        return await orchestrator.execute_single(payload, user_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/execute-multi", response_model=OrchestratorResponse)
async def execute_multiple_agents(
    payload: OrchestratorRequest,
    current_user: User = Depends(get_current_user),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator),
) -> OrchestratorResponse:
    try:
        return await orchestrator.execute_multi(payload, user_id=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

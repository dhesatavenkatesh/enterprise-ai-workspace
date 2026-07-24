from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.agents.orchestrator_service import (
    orchestrator_service,
)
from app.api.dependencies.auth import (
    get_current_user,
)

router = APIRouter(
    prefix="/api/orchestrator",
    tags=["Orchestrator"],
)


class OrchestratorRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=2,
        max_length=5000,
    )


class OrchestratorResponse(BaseModel):
    status: str
    agent: str
    tools: list[str]
    query: str
    answer: str
    duration_ms: float
    user_id: str | None = None


def get_user_id(
    current_user: Any,
) -> str | None:
    if isinstance(current_user, dict):
        value = current_user.get("id") or current_user.get("user_id")

        return str(value) if value else None

    value = getattr(current_user, "id", None) or getattr(
        current_user,
        "user_id",
        None,
    )

    return str(value) if value else None


@router.post(
    "/execute",
    response_model=OrchestratorResponse,
)
async def execute_orchestrator(
    payload: OrchestratorRequest,
    current_user: Any = Depends(
        get_current_user,
    ),
) -> OrchestratorResponse:
    result = await orchestrator_service.execute(
        query=payload.query,
        user_id=get_user_id(current_user),
    )

    return OrchestratorResponse(
        **result,
    )

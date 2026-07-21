from typing import Literal

from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from pydantic import BaseModel, Field

from app.analytics.agent_metrics import (
    agent_metrics_tracker,
)
from app.api.dependencies.auth import (
    get_current_user,
)
from app.models.user import User


router = APIRouter(
    prefix="/api/analytics/agents",
    tags=["Agent Analytics"],
)


class AgentMetricCreate(BaseModel):
    agent_name: str = Field(
        min_length=1,
        max_length=100,
    )

    status: Literal[
        "success",
        "failed",
    ]

    response_time_ms: float = Field(
        ge=0,
    )

    input_tokens: int = Field(
        default=0,
        ge=0,
    )

    output_tokens: int = Field(
        default=0,
        ge=0,
    )

    tool_names: list[str] = Field(
        default_factory=list,
    )

    workflow_id: str | None = None

    workflow_duration_ms: float | None = Field(
        default=None,
        ge=0,
    )

    error_message: str | None = None


@router.get(
    "",
    summary="Get complete agent analytics dashboard",
)
def get_agent_analytics(
    days: int = Query(
        default=7,
        ge=1,
        le=90,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
) -> dict:
    return agent_metrics_tracker.get_dashboard(
        days=days,
    )


@router.get(
    "/summary",
    summary="Get agent analytics summary",
)
def get_agent_summary(
    current_user: User = Depends(
        get_current_user,
    ),
) -> dict:
    return agent_metrics_tracker.get_summary()


@router.get(
    "/leaderboard",
    summary="Get agent leaderboard",
)
def get_agent_leaderboard(
    current_user: User = Depends(
        get_current_user,
    ),
) -> dict:
    return {
        "leaderboard": (
            agent_metrics_tracker
            .get_agent_leaderboard()
        ),
    }


@router.get(
    "/tools",
    summary="Get MCP tool usage analytics",
)
def get_tool_usage(
    current_user: User = Depends(
        get_current_user,
    ),
) -> dict:
    return {
        "tools": (
            agent_metrics_tracker.get_tool_usage()
        ),
    }


@router.get(
    "/trends",
    summary="Get agent execution trends",
)
def get_agent_trends(
    days: int = Query(
        default=7,
        ge=1,
        le=90,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
) -> dict:
    return {
        "trends": (
            agent_metrics_tracker.get_trends(
                days=days,
            )
        ),
    }


@router.get(
    "/executions",
    summary="List agent executions",
)
def get_agent_executions(
    agent_name: str | None = None,
    status: Literal[
        "success",
        "failed",
    ]
    | None = None,
    limit: int = Query(
        default=100,
        ge=1,
        le=500,
    ),
    current_user: User = Depends(
        get_current_user,
    ),
) -> dict:
    executions = (
        agent_metrics_tracker.list_executions(
            agent_name=agent_name,
            status=status,
            limit=limit,
        )
    )

    return {
        "executions": executions,
        "count": len(executions),
    }


@router.post(
    "/executions",
    summary="Record an agent execution metric",
    status_code=201,
)
def create_agent_execution_metric(
    payload: AgentMetricCreate,
    current_user: User = Depends(
        get_current_user,
    ),
) -> dict:
    metric = (
        agent_metrics_tracker.record_execution(
            agent_name=payload.agent_name,
            status=payload.status,
            response_time_ms=(
                payload.response_time_ms
            ),
            input_tokens=payload.input_tokens,
            output_tokens=payload.output_tokens,
            tool_names=payload.tool_names,
            workflow_id=payload.workflow_id,
            workflow_duration_ms=(
                payload.workflow_duration_ms
            ),
            error_message=payload.error_message,
        )
    )

    return {
        "message": (
            "Agent execution metric recorded"
        ),
        "metric": {
            **metric.__dict__,
            "total_tokens": metric.total_tokens,
        },
    }
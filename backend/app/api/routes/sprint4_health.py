from typing import Any

from fastapi import APIRouter, Depends

from app.agents.bootstrap import register_default_agents
from app.api.dependencies.auth import get_current_user
from app.mcp.bootstrap import register_default_tools
from app.models.user import User


router = APIRouter(
    prefix="/api/sprint4",
    tags=["Sprint 4 Integration"],
)


def get_item_name(item: Any) -> str:
    """
    Return the name from either:
    - a dictionary
    - a Pydantic/model object
    - another Python object
    """
    if isinstance(item, dict):
        return str(
            item.get("name")
            or item.get("tool_name")
            or item.get("agent_name")
            or "Unnamed",
        )

    return str(
        getattr(item, "name", None)
        or getattr(item, "tool_name", None)
        or getattr(item, "agent_name", None)
        or "Unnamed",
    )


@router.get(
    "/health",
    summary="Check Sprint 4 module health",
)
def sprint4_health(
    current_user: User = Depends(get_current_user),
) -> dict:
    agent_registry = register_default_agents()
    tool_registry = register_default_tools()

    agents = agent_registry.list()
    tools = tool_registry.list()

    agent_names = [
        get_item_name(agent)
        for agent in agents
    ]

    tool_names = [
        get_item_name(tool)
        for tool in tools
    ]

    return {
        "status": "healthy",
        "agents": {
            "ready": True,
            "message": (
                f"{len(agents)} agent"
                f"{'s' if len(agents) != 1 else ''} available"
            ),
            "count": len(agents),
            "names": agent_names,
        },
        "mcp": {
            "ready": True,
            "message": (
                f"{len(tools)} MCP tool"
                f"{'s' if len(tools) != 1 else ''} available"
            ),
            "count": len(tools),
            "names": tool_names,
        },
        "workflows": {
            "ready": True,
            "message": "Workflow engine is ready",
        },
        "approvals": {
            "ready": True,
            "message": "Approval engine is ready",
        },
        "user": {
            "id": getattr(current_user, "id", None),
            "email": getattr(current_user, "email", None),
        },
    }
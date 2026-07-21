from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from app.api.dependencies.auth import get_current_user
from app.mcp.bootstrap import register_default_tools
from app.mcp.executor import MCPExecutor
from app.mcp.registry import mcp_tool_registry
from app.mcp.schemas import (
    MCPHealthResponse,
    MCPToolCallRequest,
    MCPToolCallResult,
    MCPToolDefinition,
)
from app.models.user import User


router = APIRouter(
    prefix="/api/mcp",
    tags=["MCP Gateway"],
)

register_default_tools()

mcp_executor = MCPExecutor(
    registry=mcp_tool_registry,
)


@router.get(
    "/tools",
    response_model=list[MCPToolDefinition],
    summary="List MCP tools",
)
def list_mcp_tools(
    current_user: User = Depends(get_current_user),
) -> list[MCPToolDefinition]:
    return mcp_tool_registry.definitions()


@router.get(
    "/tools/{tool_name}",
    response_model=MCPToolDefinition,
    summary="Get MCP tool details",
)
def get_mcp_tool(
    tool_name: str,
    current_user: User = Depends(get_current_user),
) -> MCPToolDefinition:
    try:
        tool = mcp_tool_registry.get(tool_name)

    except KeyError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=response.model_dump(),
        )
    return response


@router.get("/health")
async def mcp_health() -> dict[str, object]:
    registry = register_default_tools()
    return {"status": "healthy", "registered_tools": len(registry.list())}

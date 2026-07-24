from datetime import UTC, datetime

from fastapi import APIRouter

router = APIRouter(
    tags=["Health"],
)


@router.get(
    "/health",
    summary="Application health check",
)
def health_check() -> dict[str, str]:
    """Return the current application health status."""

    return {
        "status": "healthy",
        "application": "Enterprise AI Workspace",
        "version": "5.0.0",
        "environment": "development",
        "timestamp": datetime.now(UTC).isoformat(),
    }

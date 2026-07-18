from fastapi import (
    APIRouter,
    Depends,
    Query,
)
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    get_current_user,
)
from app.chat.analytics_schemas import (
    ChatAnalyticsSummaryResponse,
    ChatUsageAnalyticsResponse,
)
from app.chat.analytics_service import (
    get_chat_analytics_summary,
    get_chat_usage_analytics,
)
from app.database.session import get_db
from app.models.user import User


router = APIRouter(
    prefix="/api/chat/analytics",
    tags=["Chat Analytics"],
)


@router.get(
    "/summary",
    response_model=ChatAnalyticsSummaryResponse,
)
def analytics_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
) -> ChatAnalyticsSummaryResponse:
    """
    Return overall chat statistics for the current user.
    """

    return get_chat_analytics_summary(
        db=db,
        user_id=current_user.id,
    )


@router.get(
    "/usage",
    response_model=ChatUsageAnalyticsResponse,
)
def analytics_usage(
    days: int = Query(
        default=30,
        ge=1,
        le=365,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
) -> ChatUsageAnalyticsResponse:
    """
    Return provider, model and daily usage analytics.
    """

    return get_chat_usage_analytics(
        db=db,
        user_id=current_user.id,
        days=days,
    )
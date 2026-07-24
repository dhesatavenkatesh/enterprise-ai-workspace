from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.chat.analytics_schemas import (
    ChatAnalyticsSummaryResponse,
    ChatUsageAnalyticsResponse,
    DailyChatActivity,
    ModelUsage,
    ProviderUsage,
)
from app.chat.models import (
    Conversation,
    Message,
    MessageRole,
)


def utc_now() -> datetime:
    return datetime.now(UTC)


def get_chat_analytics_summary(
    db: Session,
    user_id: int,
) -> ChatAnalyticsSummaryResponse:
    """
    Return overall chat analytics for one authenticated user.
    """

    conversation_statement = select(
        func.count(Conversation.id),
        func.count(
            case(
                (
                    Conversation.is_archived.is_(False),
                    1,
                )
            )
        ),
        func.count(
            case(
                (
                    Conversation.is_archived.is_(True),
                    1,
                )
            )
        ),
    ).where(Conversation.user_id == user_id)

    conversation_result = db.execute(conversation_statement).one()

    total_conversations = conversation_result[0] or 0
    active_conversations = conversation_result[1] or 0
    archived_conversations = conversation_result[2] or 0

    message_statement = (
        select(
            func.count(Message.id),
            func.count(
                case(
                    (
                        Message.role == MessageRole.USER,
                        1,
                    )
                )
            ),
            func.count(
                case(
                    (
                        Message.role == MessageRole.ASSISTANT,
                        1,
                    )
                )
            ),
            func.count(
                case(
                    (
                        Message.role == MessageRole.SYSTEM,
                        1,
                    )
                )
            ),
            func.coalesce(
                func.sum(Message.token_count),
                0,
            ),
            func.coalesce(
                func.sum(Message.prompt_tokens),
                0,
            ),
            func.coalesce(
                func.sum(Message.completion_tokens),
                0,
            ),
        )
        .join(
            Conversation,
            Message.conversation_id == Conversation.id,
        )
        .where(Conversation.user_id == user_id)
    )

    message_result = db.execute(message_statement).one()

    total_messages = message_result[0] or 0
    user_messages = message_result[1] or 0
    assistant_messages = message_result[2] or 0
    system_messages = message_result[3] or 0
    total_tokens = int(message_result[4] or 0)
    prompt_tokens = int(message_result[5] or 0)
    completion_tokens = int(message_result[6] or 0)

    provider_statement = (
        select(
            Message.provider,
            func.count(Message.id).label("usage_count"),
        )
        .join(
            Conversation,
            Message.conversation_id == Conversation.id,
        )
        .where(
            Conversation.user_id == user_id,
            Message.provider.is_not(None),
        )
        .group_by(Message.provider)
        .order_by(func.count(Message.id).desc())
        .limit(1)
    )

    provider_result = db.execute(provider_statement).first()

    most_used_provider = provider_result[0] if provider_result else None

    model_statement = (
        select(
            Message.model_name,
            func.count(Message.id).label("usage_count"),
        )
        .join(
            Conversation,
            Message.conversation_id == Conversation.id,
        )
        .where(
            Conversation.user_id == user_id,
            Message.model_name.is_not(None),
        )
        .group_by(Message.model_name)
        .order_by(func.count(Message.id).desc())
        .limit(1)
    )

    model_result = db.execute(model_statement).first()

    most_used_model = model_result[0] if model_result else None

    average_messages = (
        round(
            total_messages / total_conversations,
            2,
        )
        if total_conversations
        else 0.0
    )

    average_tokens = (
        round(
            total_tokens / total_conversations,
            2,
        )
        if total_conversations
        else 0.0
    )

    return ChatAnalyticsSummaryResponse(
        total_conversations=total_conversations,
        active_conversations=active_conversations,
        archived_conversations=archived_conversations,
        total_messages=total_messages,
        user_messages=user_messages,
        assistant_messages=assistant_messages,
        system_messages=system_messages,
        total_tokens=total_tokens,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        most_used_provider=most_used_provider,
        most_used_model=most_used_model,
        average_messages_per_conversation=(average_messages),
        average_tokens_per_conversation=(average_tokens),
    )


def get_chat_usage_analytics(
    db: Session,
    user_id: int,
    days: int = 30,
) -> ChatUsageAnalyticsResponse:
    """
    Return provider, model and daily activity analytics.
    """

    start_datetime = utc_now() - timedelta(days=days - 1)

    provider_statement = (
        select(
            Message.provider,
            func.count(Message.id).label("message_count"),
            func.coalesce(
                func.sum(Message.token_count),
                0,
            ).label("total_tokens"),
        )
        .join(
            Conversation,
            Message.conversation_id == Conversation.id,
        )
        .where(
            Conversation.user_id == user_id,
            Message.provider.is_not(None),
            Message.created_at >= start_datetime,
        )
        .group_by(Message.provider)
        .order_by(func.count(Message.id).desc())
    )

    provider_rows = db.execute(provider_statement).all()

    providers = [
        ProviderUsage(
            provider=row.provider,
            message_count=row.message_count,
            total_tokens=int(row.total_tokens or 0),
        )
        for row in provider_rows
    ]

    model_statement = (
        select(
            Message.model_name,
            Message.provider,
            func.count(Message.id).label("message_count"),
            func.coalesce(
                func.sum(Message.token_count),
                0,
            ).label("total_tokens"),
        )
        .join(
            Conversation,
            Message.conversation_id == Conversation.id,
        )
        .where(
            Conversation.user_id == user_id,
            Message.model_name.is_not(None),
            Message.created_at >= start_datetime,
        )
        .group_by(
            Message.model_name,
            Message.provider,
        )
        .order_by(func.count(Message.id).desc())
    )

    model_rows = db.execute(model_statement).all()

    models = [
        ModelUsage(
            model=row.model_name,
            provider=row.provider,
            message_count=row.message_count,
            total_tokens=int(row.total_tokens or 0),
        )
        for row in model_rows
    ]

    message_date = func.date(Message.created_at)

    message_activity_statement = (
        select(
            message_date.label("activity_date"),
            func.count(Message.id).label("message_count"),
            func.coalesce(
                func.sum(Message.token_count),
                0,
            ).label("total_tokens"),
        )
        .join(
            Conversation,
            Message.conversation_id == Conversation.id,
        )
        .where(
            Conversation.user_id == user_id,
            Message.created_at >= start_datetime,
        )
        .group_by(message_date)
        .order_by(message_date.asc())
    )

    message_activity_rows = db.execute(message_activity_statement).all()

    conversation_date = func.date(Conversation.created_at)

    conversation_activity_statement = (
        select(
            conversation_date.label("activity_date"),
            func.count(Conversation.id).label("conversation_count"),
        )
        .where(
            Conversation.user_id == user_id,
            Conversation.created_at >= start_datetime,
        )
        .group_by(conversation_date)
    )

    conversation_activity_rows = db.execute(conversation_activity_statement).all()

    message_activity_map = {
        row.activity_date: {
            "messages": row.message_count,
            "total_tokens": int(row.total_tokens or 0),
        }
        for row in message_activity_rows
    }

    conversation_activity_map = {
        row.activity_date: (row.conversation_count) for row in conversation_activity_rows
    }

    daily_activity: list[DailyChatActivity] = []

    for day_offset in range(days):
        current_date = start_datetime.date() + timedelta(days=day_offset)

        message_data = message_activity_map.get(
            current_date,
            {
                "messages": 0,
                "total_tokens": 0,
            },
        )

        daily_activity.append(
            DailyChatActivity(
                activity_date=current_date,
                conversations=(
                    conversation_activity_map.get(
                        current_date,
                        0,
                    )
                ),
                messages=message_data["messages"],
                total_tokens=message_data["total_tokens"],
            )
        )

    return ChatUsageAnalyticsResponse(
        days=days,
        providers=providers,
        models=models,
        daily_activity=daily_activity,
    )

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
)
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    get_current_user,
)
from app.chat.conversation_service import (
    add_message,
    create_conversation,
    delete_conversation,
    generate_conversation_title,
    get_conversation_messages,
    get_user_conversation,
    list_conversations,
    rename_conversation,
    archive_conversation,
    restore_conversation,
)
from app.chat.llm_service import (
    LLMConfigurationError,
    LLMMessage,
    LLMProviderError,
    LLMService,
    LLMServiceError,
    LLMTimeoutError,
    create_llm_provider,
)
from app.chat.models import MessageRole
from app.chat.prompt_service import (
    PromptTemplateNotFoundError,
    PromptTemplatePermissionError,
    render_prompt_template,
)
from app.chat.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationDetailResponse,
    ConversationHistoryResponse,
    ConversationSummaryResponse,
    DeleteConversationResponse,
    RenameConversationRequest,
)
from app.database.session import get_db
from app.models.user import User


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/api/chat",
    tags=["AI Chat"],
)


def create_service(
    provider_name: str | None,
    model: str | None,
) -> LLMService:
    """
    Create the configured LLM service.
    """

    provider = create_llm_provider(
        provider_name=provider_name,
        model=model,
    )

    return LLMService(provider=provider)


def build_llm_messages(
    db: Session,
    conversation_id: UUID,
    user_id: int,
    system_prompt: str | None = None,
    latest_user_prompt_override: str | None = None,
) -> list[LLMMessage]:
    """
    Build the complete LLM conversation context.

    The original user message remains stored in the database.
    When a prompt template is selected, only the latest user
    message sent to the LLM is replaced by the rendered template.
    """

    messages: list[LLMMessage] = []

    if system_prompt:
        messages.append(
            LLMMessage(
                role="system",
                content=system_prompt,
            )
        )

    stored_messages = get_conversation_messages(
        db,
        conversation_id,
        user_id,
    )

    latest_user_message_index: int | None = None

    for stored_message in stored_messages:
        messages.append(
            LLMMessage(
                role=stored_message.role.value,
                content=stored_message.content,
            )
        )

        if stored_message.role == MessageRole.USER:
            latest_user_message_index = (
                len(messages) - 1
            )

    if (
        latest_user_prompt_override
        and latest_user_message_index is not None
    ):
        messages[latest_user_message_index] = (
            LLMMessage(
                role="user",
                content=latest_user_prompt_override,
            )
        )

    return messages


def get_or_create_conversation(
    db: Session,
    user_id: int,
    request_data: ChatRequest,
):
    """
    Return the requested conversation or create a new one.
    """

    if request_data.conversation_id:
        return get_user_conversation(
            db,
            request_data.conversation_id,
            user_id,
        )

    title = generate_conversation_title(
        request_data.prompt
    )

    return create_conversation(
        db,
        user_id,
        title,
    )


def prepare_prompt_for_llm(
    db: Session,
    user_id: int,
    request_data: ChatRequest,
) -> str | None:
    """
    Render the selected prompt template.

    Returns None when the request does not contain template_id.
    """

    if request_data.template_id is None:
        return None

    return render_prompt_template(
        db=db,
        template_id=request_data.template_id,
        user_id=user_id,
        question=request_data.prompt,
    )


def raise_prompt_template_http_error(
    exc: Exception,
) -> None:
    """
    Convert prompt-template service errors into HTTP errors.
    """

    if isinstance(
        exc,
        PromptTemplateNotFoundError,
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    if isinstance(
        exc,
        PromptTemplatePermissionError,
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(exc),
        ) from exc

    raise exc


@router.post(
    "",
    response_model=ChatResponse,
)
async def chat(
    request_data: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
) -> ChatResponse:
    """
    Generate a normal AI chat response.

    The request may optionally contain template_id.
    """

    try:
        conversation = get_or_create_conversation(
            db=db,
            user_id=current_user.id,
            request_data=request_data,
        )

        # Store the user's original question.
        # This keeps conversation history readable.
        add_message(
            db=db,
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=request_data.prompt,
        )

        # Ensure the latest user message is available
        # before building the LLM context.
        db.flush()

        rendered_template_prompt = (
            prepare_prompt_for_llm(
                db=db,
                user_id=current_user.id,
                request_data=request_data,
            )
        )

        llm_messages = build_llm_messages(
            db=db,
            conversation_id=conversation.id,
            user_id=current_user.id,
            system_prompt=(
                request_data.system_prompt
            ),
            latest_user_prompt_override=(
                rendered_template_prompt
            ),
        )

        llm_service = create_service(
            provider_name=request_data.provider,
            model=request_data.model,
        )

        llm_response = await llm_service.generate(
            messages=llm_messages,
            temperature=request_data.temperature,
            max_tokens=request_data.max_tokens,
        )

        add_message(
            db=db,
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=llm_response.content,
            token_count=llm_response.total_tokens,
            prompt_tokens=(
                llm_response.prompt_tokens
            ),
            completion_tokens=(
                llm_response.completion_tokens
            ),
            provider=llm_response.provider,
            model_name=llm_response.model,
        )

        db.commit()

        return ChatResponse(
            conversation_id=conversation.id,
            response=llm_response.content,
            tokens=llm_response.total_tokens,
            prompt_tokens=(
                llm_response.prompt_tokens
            ),
            completion_tokens=(
                llm_response.completion_tokens
            ),
            provider=llm_response.provider,
            model=llm_response.model,
        )

    except (
        PromptTemplateNotFoundError,
        PromptTemplatePermissionError,
    ) as exc:
        db.rollback()
        raise_prompt_template_http_error(exc)

    except (
        LLMConfigurationError,
        LLMProviderError,
        LLMTimeoutError,
    ) as exc:
        db.rollback()

        logger.exception(
            "LLM chat generation error"
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                f"{type(exc).__name__}: {str(exc)}"
            ),
        ) from exc

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()

        logger.exception(
            "Unexpected chat generation error"
        )

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                f"{type(exc).__name__}: {str(exc)}"
            ),
        ) from exc


@router.post("/stream")
async def stream_chat(
    request_data: ChatRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
) -> StreamingResponse:
    """
    Stream an AI response using Server-Sent Events.

    Prompt templates are supported through template_id.
    """

    try:
        conversation = get_or_create_conversation(
            db=db,
            user_id=current_user.id,
            request_data=request_data,
        )

        # Save the original user question.
        add_message(
            db=db,
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=request_data.prompt,
        )

        db.flush()

        rendered_template_prompt = (
            prepare_prompt_for_llm(
                db=db,
                user_id=current_user.id,
                request_data=request_data,
            )
        )

        llm_messages = build_llm_messages(
            db=db,
            conversation_id=conversation.id,
            user_id=current_user.id,
            system_prompt=(
                request_data.system_prompt
            ),
            latest_user_prompt_override=(
                rendered_template_prompt
            ),
        )

        llm_service = create_service(
            provider_name=request_data.provider,
            model=request_data.model,
        )

        # Save the user message and template usage before
        # beginning the response stream.
        db.commit()

    except (
        PromptTemplateNotFoundError,
        PromptTemplatePermissionError,
    ) as exc:
        db.rollback()
        raise_prompt_template_http_error(exc)

    except LLMServiceError as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()

        logger.exception(
            "Unable to start streaming chat"
        )

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                f"Unable to start streaming: "
                f"{type(exc).__name__}: {str(exc)}"
            ),
        ) from exc

    async def event_generator() -> AsyncIterator[str]:
        complete_response = ""

        try:
            start_event = {
                "type": "start",
                "conversation_id": str(
                    conversation.id
                ),
                "provider": (
                    llm_service.provider.provider_name
                ),
                "model": (
                    llm_service.provider.model
                ),
                "template_id": (
                    str(request_data.template_id)
                    if request_data.template_id
                    else None
                ),
            }

            yield (
                "event: start\n"
                f"data: {json.dumps(start_event)}\n\n"
            )

            yield (
                "event: typing\n"
                'data: {"typing": true}\n\n'
            )

            async for chunk in llm_service.stream(
                messages=llm_messages,
                temperature=(
                    request_data.temperature
                ),
                max_tokens=(
                    request_data.max_tokens
                ),
            ):
                if await request.is_disconnected():
                    logger.info(
                        "Client disconnected from "
                        "conversation %s",
                        conversation.id,
                    )
                    return

                complete_response += chunk

                token_event = {
                    "type": "token",
                    "content": chunk,
                }

                yield (
                    "event: token\n"
                    f"data: {json.dumps(token_event)}\n\n"
                )

                await asyncio.sleep(0)

            if complete_response.strip():
                add_message(
                    db=db,
                    conversation_id=conversation.id,
                    role=MessageRole.ASSISTANT,
                    content=complete_response,
                    provider=(
                        llm_service
                        .provider
                        .provider_name
                    ),
                    model_name=(
                        llm_service.provider.model
                    ),
                )

                db.commit()

            yield (
                "event: typing\n"
                'data: {"typing": false}\n\n'
            )

            complete_event = {
                "type": "complete",
                "conversation_id": str(
                    conversation.id
                ),
                "response": complete_response,
            }

            yield (
                "event: complete\n"
                f"data: {json.dumps(complete_event)}\n\n"
            )

        except asyncio.CancelledError:
            db.rollback()
            raise

        except LLMServiceError as exc:
            db.rollback()

            error_event = {
                "type": "error",
                "message": str(exc),
            }

            yield (
                "event: error\n"
                f"data: {json.dumps(error_event)}\n\n"
            )

        except Exception as exc:
            db.rollback()

            logger.exception(
                "Unexpected streaming error"
            )

            error_event = {
                "type": "error",
                "message": (
                    f"The AI response stream failed: "
                    f"{type(exc).__name__}: {str(exc)}"
                ),
            }

            yield (
                "event: error\n"
                f"data: {json.dumps(error_event)}\n\n"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get(
    "/conversations",
    response_model=ConversationHistoryResponse,
)
@router.get(
    "/history",
    response_model=ConversationHistoryResponse,
    include_in_schema=False,
)
def chat_history(
    page: int = Query(
        default=1,
        ge=1,
    ),
    page_size: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    search: str | None = Query(
        default=None,
        max_length=255,
    ),
    archived: bool = Query(
        default=False,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
) -> ConversationHistoryResponse:
    """
    Return paginated conversation history.
    """

    result = list_conversations(
        db=db,
        user_id=current_user.id,
        page=page,
        page_size=page_size,
        search=search,
        archived=archived,
    )

    return ConversationHistoryResponse(
        **result
    )


@router.get(
    "/{conversation_id}",
    response_model=ConversationDetailResponse,
)
def get_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
) -> ConversationDetailResponse:
    """
    Return one conversation and its messages.
    """

    conversation = get_user_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
        include_messages=True,
    )

    return ConversationDetailResponse.model_validate(
        conversation
    )


@router.delete(
    "/{conversation_id}",
    response_model=DeleteConversationResponse,
)
def remove_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
) -> DeleteConversationResponse:
    """
    Delete one conversation.
    """

    delete_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    db.commit()

    return DeleteConversationResponse(
        message="Conversation deleted successfully",
        conversation_id=conversation_id,
    )


@router.put(
    "/{conversation_id}/rename",
    response_model=ConversationSummaryResponse,
)
def update_conversation_title(
    conversation_id: UUID,
    request_data: RenameConversationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
) -> ConversationSummaryResponse:
    """
    Rename one conversation.
    """

    conversation = rename_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
        title=request_data.title,
    )

    db.commit()
    db.refresh(conversation)

    return ConversationSummaryResponse.model_validate(
        conversation
    )

@router.put(
    "/{conversation_id}/archive",
    response_model=ConversationSummaryResponse,
)
def archive_user_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
) -> ConversationSummaryResponse:
    conversation = archive_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    db.commit()
    db.refresh(conversation)

    return ConversationSummaryResponse.model_validate(
        conversation
    )

@router.put(
    "/{conversation_id}/restore",
    response_model=ConversationSummaryResponse,
)
def restore_user_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
) -> ConversationSummaryResponse:
    conversation = restore_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=current_user.id,
    )

    db.commit()
    db.refresh(conversation)

    return ConversationSummaryResponse.model_validate(
        conversation
    )


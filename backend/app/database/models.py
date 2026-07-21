"""SQLAlchemy model registry."""

from app.models.user import User  # noqa: F401
from app.models.role import Role  # noqa: F401
from app.models.permission import Permission  # noqa: F401
from app.models.role_permission import RolePermission  # noqa: F401
from app.models.user_session import UserSession  # noqa: F401

from app.models.document import Document  # noqa: F401
from app.models.document_chunk import DocumentChunk  # noqa: F401

from app.chat.models import (  # noqa: F401
    Conversation,
    Message,
    PromptTemplate,
)


__all__ = [
    "User",
    "Role",
    "Permission",
    "RolePermission",
    "UserSession",
    "Conversation",
    "Message",
    "PromptTemplate",
    "Document",
    "DocumentChunk",
]
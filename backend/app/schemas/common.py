from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    errors: list[dict[str, Any]] | None = None


class SuccessResponse(BaseModel):
    success: bool = True
    message: str
    data: Any | None = None

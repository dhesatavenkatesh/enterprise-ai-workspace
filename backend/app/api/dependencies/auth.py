from fastapi import (
    Depends,
    HTTPException,
    status,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from app.auth.jwt import decode_access_token
from app.database.session import get_db
from app.models.user import User
from app.services.auth_service import get_user_by_id


security = HTTPBearer(
    auto_error=False
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials
    | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    try:
        payload = decode_access_token(
            credentials.credentials
        )

        user_id = int(payload["sub"])

    except (
        ValueError,
        KeyError,
        TypeError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        ) from exc

    user = get_user_by_id(
        db,
        user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if user.is_deleted:
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User account has been deleted",
    )

    if user.is_locked:
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User account is locked",
    )

    if not user.is_active:
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User account is inactive",
    )

    if user.status.lower() != "active":
        raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User account is unavailable",
    )

    return user
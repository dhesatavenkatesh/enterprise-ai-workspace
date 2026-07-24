from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from jose import JWTError, jwt

from app.core.config import settings


def create_access_token(
    subject: str,
    role: str,
) -> tuple[str, datetime]:
    expire = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)

    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "type": "access",
        "jti": str(uuid4()),
        "iat": datetime.now(UTC),
        "exp": expire,
    }

    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return token, expire


def create_refresh_token(
    subject: str,
    role: str,
) -> tuple[str, datetime]:
    expire = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)

    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "type": "refresh",
        "jti": str(uuid4()),
        "iat": datetime.now(UTC),
        "exp": expire,
    }

    token = jwt.encode(
        payload,
        settings.jwt_refresh_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    return token, expire


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        if payload.get("type") != "access":
            raise JWTError("Invalid token type")

        return payload

    except JWTError as exc:
        raise ValueError("Invalid or expired access token") from exc


def decode_refresh_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_refresh_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

        if payload.get("type") != "refresh":
            raise JWTError("Invalid token type")

        return payload

    except JWTError as exc:
        raise ValueError("Invalid or expired refresh token") from exc

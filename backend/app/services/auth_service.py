from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.auth.jwt import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.auth.password import (
    hash_password,
    verify_password,
)
from app.auth.token import (
    hash_token,
    verify_token_hash,
)
from app.core.config import settings
from app.models.role import Role
from app.models.user import User
from app.models.user_session import UserSession
from app.schemas.auth import (
    AuthUserResponse,
    LoginRequest,
    RegisterRequest,
    TokenResponse,
)


def build_user_response(
    user: User,
) -> AuthUserResponse:
    return AuthUserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=user.role.name,
        status=user.status,
    )


def get_user_by_email(
    db: Session,
    email: str,
) -> User | None:
    statement = (
        select(User)
        .options(joinedload(User.role))
        .where(User.email == email.lower())
    )

    return db.scalar(statement)


def get_user_by_id(
    db: Session,
    user_id: int,
) -> User | None:
    statement = (
        select(User)
        .options(joinedload(User.role))
        .where(User.id == user_id)
    )

    return db.scalar(statement)


def register_user(
    db: Session,
    request: RegisterRequest,
) -> AuthUserResponse:
    existing_user = get_user_by_email(
        db,
        request.email,
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    employee_role = db.scalar(
        select(Role).where(
            Role.name == "Employee"
        )
    )

    if employee_role is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default Employee role is missing",
        )

    try:
        user = User(
            name=request.name.strip(),
            email=request.email.lower(),
            password_hash=hash_password(
                request.password
            ),
            role_id=employee_role.id,
            status="active",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        user.role = employee_role

        return build_user_response(user)

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User registration failed",
        ) from exc


def login_user(
    db: Session,
    request: LoginRequest,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> TokenResponse:
    user = get_user_by_email(
        db,
        request.email,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(
        request.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
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

    access_token, _ = create_access_token(
        subject=str(user.id),
        role=user.role.name,
    )

    refresh_token, refresh_expiry = (
        create_refresh_token(
            subject=str(user.id),
            role=user.role.name,
        )
    )

    session = UserSession(
        user_id=user.id,
        refresh_token_hash=hash_token(
            refresh_token
        ),
        expiry=refresh_expiry,
        ip_address=ip_address,
        user_agent=user_agent,
    )

    try:
        db.add(user)
        db.add(session)
        db.commit()

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login session creation failed",
        ) from exc

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=(
            settings.access_token_expire_minutes * 60
        ),
        user=build_user_response(user),
    )


def refresh_user_session(
    db: Session,
    refresh_token: str,
) -> TokenResponse:
    try:
        payload = decode_refresh_token(
            refresh_token
        )

        user_id = int(payload["sub"])

    except (
        ValueError,
        KeyError,
        TypeError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
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

    if user.status.lower() != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    current_time = datetime.now(timezone.utc)

    sessions = db.scalars(
        select(UserSession).where(
            UserSession.user_id == user.id,
            UserSession.revoked_at.is_(None),
            UserSession.expiry > current_time,
        )
    ).all()

    matching_session = next(
        (
            session
            for session in sessions
            if verify_token_hash(
                refresh_token,
                session.refresh_token_hash,
            )
        ),
        None,
    )

    if matching_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh session is invalid or revoked",
        )

    matching_session.revoked_at = current_time

    new_access_token, _ = create_access_token(
        subject=str(user.id),
        role=user.role.name,
    )

    new_refresh_token, new_refresh_expiry = (
        create_refresh_token(
            subject=str(user.id),
            role=user.role.name,
        )
    )

    new_session = UserSession(
        user_id=user.id,
        refresh_token_hash=hash_token(
            new_refresh_token
        ),
        expiry=new_refresh_expiry,
        ip_address=matching_session.ip_address,
        user_agent=matching_session.user_agent,
    )

    try:
        db.add(new_session)
        db.commit()

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed",
        ) from exc

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=(
            settings.access_token_expire_minutes * 60
        ),
        user=build_user_response(user),
    )


def logout_user(
    db: Session,
    refresh_token: str,
) -> None:
    try:
        payload = decode_refresh_token(
            refresh_token
        )

        user_id = int(payload["sub"])

    except (
        ValueError,
        KeyError,
        TypeError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        ) from exc

    sessions = db.scalars(
        select(UserSession).where(
            UserSession.user_id == user_id,
            UserSession.revoked_at.is_(None),
        )
    ).all()

    matching_session = next(
        (
            session
            for session in sessions
            if verify_token_hash(
                refresh_token,
                session.refresh_token_hash,
            )
        ),
        None,
    )

    if matching_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is invalid or already revoked",
        )

    matching_session.revoked_at = (
        datetime.now(timezone.utc)
    )

    try:
        db.commit()

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed",
        ) from exc
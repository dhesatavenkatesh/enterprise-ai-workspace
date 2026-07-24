from fastapi import (
    APIRouter,
    Depends,
    Request,
    status,
)
from sqlalchemy.orm import Session

from app.api.dependencies.auth import (
    get_current_user,
)
from app.database.session import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthUserResponse,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    TokenResponse,
)
from app.services.auth_service import (
    build_user_response,
    login_user,
    logout_user,
    refresh_user_session,
    register_user,
)

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=AuthUserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
) -> AuthUserResponse:
    return register_user(
        db,
        request,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    request_data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> TokenResponse:
    client_ip = request.client.host if request.client else None

    user_agent = request.headers.get("user-agent")

    return login_user(
        db=db,
        request=request_data,
        ip_address=client_ip,
        user_agent=user_agent,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    return refresh_user_session(
        db,
        request.refresh_token,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
)
def logout(
    request: LogoutRequest,
    db: Session = Depends(get_db),
) -> MessageResponse:
    logout_user(
        db,
        request.refresh_token,
    )

    return MessageResponse(message="Logout successful")


@router.get(
    "/me",
    response_model=AuthUserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
) -> AuthUserResponse:
    return build_user_response(current_user)

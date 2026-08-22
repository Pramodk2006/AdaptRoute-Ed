"""
Auth router — /api/v1/auth endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(UserRepository(db))


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
    summary="Register a new user account",
)
def register(
    payload: RegisterRequest,
    service: AuthService = Depends(_get_auth_service),
) -> UserResponse:
    return service.register(payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and receive JWT tokens",
)
def login(
    payload: LoginRequest,
    service: AuthService = Depends(_get_auth_service),
) -> TokenResponse:
    return service.login(payload)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Exchange a refresh token for a new access token",
)
def refresh_token(
    payload: RefreshRequest,
    service: AuthService = Depends(_get_auth_service),
) -> TokenResponse:
    return service.refresh(payload.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the currently authenticated user",
)
def get_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserResponse:
    service = AuthService(UserRepository(db))
    return service.get_me(current_user)

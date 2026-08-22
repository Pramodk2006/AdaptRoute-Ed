"""
AuthService — business logic for user registration, login, and token refresh.
"""
from app.config import get_settings
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.utils.logger import logger

from fastapi import HTTPException, status

settings = get_settings()


class AuthService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    def register(self, payload: RegisterRequest) -> UserResponse:
        """
        Create a new user account.
        Raises HTTP 409 if email or username is already taken.
        """
        if self.user_repo.email_exists(payload.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists.",
            )
        if self.user_repo.username_exists(payload.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This username is already taken.",
            )

        hashed = hash_password(payload.password)
        user = self.user_repo.create(
            email=payload.email,
            username=payload.username,
            hashed_password=hashed,
        )
        logger.info(f"New user registered: {user.email} (id={user.id})")

        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            created_at=user.created_at,
            has_profile=False,
        )

    def login(self, payload: LoginRequest) -> TokenResponse:
        """
        Authenticate a user and return JWT access + refresh tokens.
        Raises HTTP 401 on bad credentials.
        """
        user = self.user_repo.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account has been deactivated.",
            )

        subject = str(user.id)
        logger.info(f"User logged in: {user.email}")

        return TokenResponse(
            access_token=create_access_token(subject),
            refresh_token=create_refresh_token(subject),
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    def refresh(self, refresh_token: str) -> TokenResponse:
        """
        Issue a new access token from a valid refresh token.
        Raises HTTP 401 if the refresh token is invalid or expired.
        """
        payload = decode_token(refresh_token)
        if payload is None or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token.",
            )

        user_id = payload.get("sub")
        user = self.user_repo.get_by_id(user_id)
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or deactivated.",
            )

        return TokenResponse(
            access_token=create_access_token(str(user.id)),
            refresh_token=create_refresh_token(str(user.id)),
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

    def get_me(self, user: User) -> UserResponse:
        """Return current user's public profile, flagging whether they have a learner profile."""
        return UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            created_at=user.created_at,
            has_profile=user.profile is not None,
        )

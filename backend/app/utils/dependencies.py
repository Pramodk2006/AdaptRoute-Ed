"""
FastAPI dependency factories for dependency injection.
"""
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.utils.security import decode_token
from app.utils.logger import logger

bearer_scheme = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Decode the JWT from the Authorization header and return the
    corresponding User ORM instance.

    Raises HTTP 401 if the token is missing, invalid, or the user
    no longer exists in the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(credentials.credentials)
    if payload is None:
        raise credentials_exception

    if payload.get("type") != "access":
        raise credentials_exception

    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user: Optional[User] = db.get(User, UUID(user_id))
    if user is None:
        logger.warning(f"Token valid but user not found: {user_id}")
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account has been deactivated.",
        )

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Alias to get_current_user; kept for clarity in route signatures."""
    return current_user

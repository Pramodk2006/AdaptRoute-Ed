"""
JWT creation/verification and password hashing utilities.
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings
from app.utils.logger import logger

settings = get_settings()

# ── Password Hashing ───────────────────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """Return a bcrypt hash of the given plain-text password."""
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ── JWT Token Helpers ──────────────────────────────────────────────────────────
def _create_token(data: Dict[str, Any], expires_delta: timedelta) -> str:
    """Internal helper to build a signed JWT."""
    payload = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    payload.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: str) -> str:
    """
    Create a short-lived access token.
    ``subject`` is the user's UUID string.
    """
    delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token({"sub": subject, "type": "access"}, delta)


def create_refresh_token(subject: str) -> str:
    """Create a long-lived refresh token."""
    delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return _create_token({"sub": subject, "type": "refresh"}, delta)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and verify a JWT.
    Returns the payload dict or None if invalid/expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError as exc:
        logger.warning(f"JWT decode failed: {exc}")
        return None

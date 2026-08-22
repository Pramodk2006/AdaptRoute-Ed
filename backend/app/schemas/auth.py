"""
Pydantic schemas for authentication endpoints.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Request Schemas ────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    """POST /auth/register"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter.")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit.")
        return v


class LoginRequest(BaseModel):
    """POST /auth/login"""
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    """POST /auth/refresh"""
    refresh_token: str


# ── Response Schemas ───────────────────────────────────────────────────────────

class TokenResponse(BaseModel):
    """Returned after successful login or token refresh."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int          # seconds until access_token expiry


class UserResponse(BaseModel):
    """Public representation of a user account."""
    id: uuid.UUID
    email: str
    username: str
    is_active: bool
    created_at: datetime
    has_profile: bool = False   # Populated by service layer

    model_config = {"from_attributes": True}

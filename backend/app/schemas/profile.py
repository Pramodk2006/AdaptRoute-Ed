"""
Pydantic schemas for learner profile endpoints.
"""
import uuid
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


SkillLevel = Literal["beginner", "intermediate", "advanced"]
PreferredPace = Literal["slow", "moderate", "fast"]


# ── Request Schemas ────────────────────────────────────────────────────────────

class ProfileCreateRequest(BaseModel):
    """POST /profile"""
    full_name: str = Field(..., min_length=2, max_length=200)
    skill_level: SkillLevel
    learning_goal: str = Field(..., min_length=10, max_length=1000)
    preferred_pace: PreferredPace
    daily_study_time: int = Field(..., ge=15, le=480, description="Minutes per day (15–480)")


class ProfileUpdateRequest(BaseModel):
    """PUT /profile — all fields optional for partial updates"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=200)
    skill_level: Optional[SkillLevel] = None
    learning_goal: Optional[str] = Field(None, min_length=10, max_length=1000)
    preferred_pace: Optional[PreferredPace] = None
    daily_study_time: Optional[int] = Field(None, ge=15, le=480)


# ── Response Schemas ───────────────────────────────────────────────────────────

class ProfileResponse(BaseModel):
    """GET /profile"""
    id: uuid.UUID
    user_id: uuid.UUID
    full_name: str
    skill_level: str
    learning_goal: str
    preferred_pace: str
    daily_study_time: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

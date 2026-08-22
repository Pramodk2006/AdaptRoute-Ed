"""
ProfileRepository — all DB operations involving LearnerProfile.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.learner_profile import LearnerProfile
from app.schemas.profile import ProfileCreateRequest, ProfileUpdateRequest


class ProfileRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_user_id(self, user_id: UUID) -> Optional[LearnerProfile]:
        return (
            self.db.query(LearnerProfile)
            .filter(LearnerProfile.user_id == user_id)
            .first()
        )

    def create(self, user_id: UUID, payload: ProfileCreateRequest) -> LearnerProfile:
        profile = LearnerProfile(
            user_id=user_id,
            full_name=payload.full_name,
            skill_level=payload.skill_level,
            learning_goal=payload.learning_goal,
            preferred_pace=payload.preferred_pace,
            daily_study_time=payload.daily_study_time,
        )
        self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile

    def update(self, profile: LearnerProfile, payload: ProfileUpdateRequest) -> LearnerProfile:
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        self.db.commit()
        self.db.refresh(profile)
        return profile

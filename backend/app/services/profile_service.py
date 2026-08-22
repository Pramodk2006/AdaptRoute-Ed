"""
ProfileService — business logic for learner profile management.
"""
from uuid import UUID

from fastapi import HTTPException, status

from app.models.user import User
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfileCreateRequest, ProfileUpdateRequest, ProfileResponse
from app.utils.logger import logger


class ProfileService:
    def __init__(self, repo: ProfileRepository) -> None:
        self.repo = repo

    def create_profile(self, user: User, payload: ProfileCreateRequest) -> ProfileResponse:
        if self.repo.get_by_user_id(user.id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Profile already exists. Use PUT to update.",
            )
        profile = self.repo.create(user.id, payload)
        logger.info(f"Profile created for user {user.id}")
        return ProfileResponse.model_validate(profile)

    def get_profile(self, user: User) -> ProfileResponse:
        profile = self.repo.get_by_user_id(user.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found. Please create your profile first.",
            )
        return ProfileResponse.model_validate(profile)

    def update_profile(self, user: User, payload: ProfileUpdateRequest) -> ProfileResponse:
        profile = self.repo.get_by_user_id(user.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found. Create it first via POST /profile.",
            )
        updated = self.repo.update(profile, payload)
        return ProfileResponse.model_validate(updated)

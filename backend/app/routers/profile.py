"""Profile router — /api/v1/profile endpoints."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfileCreateRequest, ProfileUpdateRequest, ProfileResponse
from app.services.profile_service import ProfileService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/profile", tags=["Profile"])


def _svc(db: Session = Depends(get_db)) -> ProfileService:
    return ProfileService(ProfileRepository(db))


@router.post("", response_model=ProfileResponse, status_code=201,
             summary="Create learner profile")
def create_profile(
    payload: ProfileCreateRequest,
    user: User = Depends(get_current_user),
    svc: ProfileService = Depends(_svc),
):
    return svc.create_profile(user, payload)


@router.get("", response_model=ProfileResponse, summary="Get learner profile")
def get_profile(
    user: User = Depends(get_current_user),
    svc: ProfileService = Depends(_svc),
):
    return svc.get_profile(user)


@router.put("", response_model=ProfileResponse, summary="Update learner profile")
def update_profile(
    payload: ProfileUpdateRequest,
    user: User = Depends(get_current_user),
    svc: ProfileService = Depends(_svc),
):
    return svc.update_profile(user, payload)

"""Quiz router — /api/v1/quiz endpoints."""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.repositories.profile_repository import ProfileRepository
from app.repositories.quiz_repository import QuizRepository
from app.repositories.roadmap_repository import RoadmapRepository
from app.schemas.roadmap import (
    QuizResponse, QuizSubmitRequest, QuizAttemptResponse,
)
from app.services.quiz_service import QuizService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/quiz", tags=["Quiz"])


def _svc(db: Session = Depends(get_db)) -> QuizService:
    return QuizService(QuizRepository(db), RoadmapRepository(db), ProfileRepository(db), db=db)


@router.post("/generate/{topic_id}", response_model=QuizResponse, status_code=201,
             summary="Generate a quiz for a topic via LLM")
async def generate_quiz(
    topic_id: UUID,
    user: User = Depends(get_current_user),
    svc: QuizService = Depends(_svc),
):
    return await svc.generate_quiz(user, topic_id)


@router.get("/{topic_id}", response_model=QuizResponse,
            summary="Get quiz for a topic")
def get_quiz(
    topic_id: UUID,
    user: User = Depends(get_current_user),
    svc: QuizService = Depends(_svc),
):
    return svc.get_quiz(user, topic_id)


@router.post("/{quiz_id}/submit", response_model=QuizAttemptResponse,
             summary="Submit quiz answers and get results")
def submit_quiz(
    quiz_id: UUID,
    payload: QuizSubmitRequest,
    user: User = Depends(get_current_user),
    svc: QuizService = Depends(_svc),
):
    return svc.submit_quiz(user, quiz_id, payload)


@router.get("/attempts/{attempt_id}", response_model=QuizAttemptResponse,
            summary="Get a specific quiz attempt with results")
def get_attempt(
    attempt_id: UUID,
    user: User = Depends(get_current_user),
    svc: QuizService = Depends(_svc),
):
    return svc.get_attempt(user, attempt_id)

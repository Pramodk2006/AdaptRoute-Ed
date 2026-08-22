"""Dashboard router — /api/v1/dashboard."""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.roadmap import Roadmap
from app.models.progress import Progress
from app.models.quiz_attempt import QuizAttempt
from app.schemas.roadmap import DashboardResponse
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse, summary="Get aggregated dashboard stats")
def get_dashboard(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Get active roadmap
    roadmap: Roadmap | None = (
        db.query(Roadmap)
        .filter(Roadmap.user_id == user.id, Roadmap.status == "active")
        .order_by(Roadmap.created_at.desc())
        .first()
    )

    # Get progress for active roadmap
    progress: Progress | None = None
    if roadmap:
        progress = (
            db.query(Progress)
            .filter(Progress.roadmap_id == roadmap.id)
            .first()
        )

    # Count total quiz attempts
    total_attempts: int = (
        db.query(func.count(QuizAttempt.id))
        .filter(QuizAttempt.user_id == user.id)
        .scalar()
        or 0
    )

    return DashboardResponse(
        completed_topics=progress.completed_topics if progress else 0,
        total_topics=progress.total_topics if progress else 0,
        completion_percentage=progress.completion_percentage if progress else 0.0,
        average_quiz_score=progress.average_quiz_score if progress else 0.0,
        total_quiz_attempts=total_attempts,
        last_activity=progress.last_activity if progress else None,
        roadmap_status=roadmap.status if roadmap else None,
        roadmap_title=roadmap.title if roadmap else None,
    )

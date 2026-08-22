"""
Knowledge router — API endpoints for topic mastery tracking and adaptive remediation.
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.repositories.mastery_repository import MasteryRepository
from app.services.remediation_service import RemediationService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/knowledge", tags=["Knowledge Tracing"])


# ── Response Schemas ──────────────────────────────────────────────────────────

class TopicMasteryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    topic_id: str
    mastery_score: float
    mastery_level: str
    attempts_count: int
    correct_count: int
    accuracy_pct: float
    last_attempt_at: Optional[str]


class MasteryStatsOut(BaseModel):
    topics_tracked: int
    avg_mastery: float
    mastered_count: int
    proficient_count: int
    developing_count: int
    struggling_count: int
    overall_readiness: float
    topic_details: List[TopicMasteryOut]


class RemediationRequest(BaseModel):
    topic_title: str
    skill_level: str = "beginner"
    missed_concepts: List[str] = []


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/mastery", response_model=MasteryStatsOut)
def get_mastery_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get student's topic mastery stats and per-topic BKT scores."""
    repo = MasteryRepository(db)
    stats = repo.get_mastery_stats(user_id=current_user.id)
    records = repo.get_user_mastery(user_id=current_user.id)

    topic_details = [
        TopicMasteryOut(
            topic_id=str(r.topic_id),
            mastery_score=r.mastery_score,
            mastery_level=r.mastery_level,
            attempts_count=r.attempts_count,
            correct_count=r.correct_count,
            accuracy_pct=r.accuracy_pct,
            last_attempt_at=r.last_attempt_at.isoformat() if r.last_attempt_at else None,
        )
        for r in records
    ]

    return MasteryStatsOut(**stats, topic_details=topic_details)


@router.post("/remediation/{topic_id}")
async def generate_remediation(
    topic_id: str,
    body: RemediationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate adaptive remediation notes for a topic the student is struggling with."""
    try:
        topic_uuid = uuid.UUID(topic_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid topic_id format.")

    service = RemediationService(db)
    notes = await service.generate_remediation_notes(
        user_id=current_user.id,
        topic_id=topic_uuid,
        topic_title=body.topic_title,
        skill_level=body.skill_level,
        missed_concepts=body.missed_concepts,
    )
    return {"topic_id": topic_id, "remediation_notes": notes}

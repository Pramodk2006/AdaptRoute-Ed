"""Roadmap router — /api/v1/roadmap and /api/v1/content and /api/v1/topics."""
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.repositories.profile_repository import ProfileRepository
from app.repositories.roadmap_repository import RoadmapRepository
from app.schemas.roadmap import (
    GenerateRoadmapRequest, RoadmapResponse,
    TopicContentResponse, TopicResponse,
)
from app.services.roadmap_service import RoadmapService
from app.utils.dependencies import get_current_user

router = APIRouter(tags=["Roadmap & Content"])


def _svc(db: Session = Depends(get_db)) -> RoadmapService:
    return RoadmapService(RoadmapRepository(db), ProfileRepository(db))


# ── Roadmap ────────────────────────────────────────────────────

@router.post("/roadmap/generate", response_model=RoadmapResponse, status_code=201,
             summary="Generate personalised roadmap via LLM")
async def generate_roadmap(
    payload: GenerateRoadmapRequest,
    user: User = Depends(get_current_user),
    svc: RoadmapService = Depends(_svc),
):
    return await svc.generate_roadmap(user, payload)


@router.get("/roadmap", response_model=RoadmapResponse,
            summary="Get active roadmap")
def get_roadmap(
    user: User = Depends(get_current_user),
    svc: RoadmapService = Depends(_svc),
):
    return svc.get_roadmap(user)


# ── Topics ─────────────────────────────────────────────────────

@router.put("/topics/{topic_id}/complete", response_model=TopicResponse,
            summary="Mark a topic as completed")
def complete_topic(
    topic_id: UUID,
    user: User = Depends(get_current_user),
    svc: RoadmapService = Depends(_svc),
):
    return svc.complete_topic(user, topic_id)


# ── Content ────────────────────────────────────────────────────

from fastapi.responses import StreamingResponse

@router.post("/content/generate/{topic_id}", response_model=TopicContentResponse,
             status_code=201, summary="Generate study content for a topic")
async def generate_content(
    topic_id: UUID,
    user: User = Depends(get_current_user),
    svc: RoadmapService = Depends(_svc),
):
    return await svc.generate_content(user, topic_id, force=True)


@router.post("/content/generate/stream/{topic_id}", summary="Stream real-time study content tokens for a topic")
async def generate_content_stream(
    topic_id: UUID,
    user: User = Depends(get_current_user),
    svc: RoadmapService = Depends(_svc),
):
    """Real-time SSE token streaming endpoint for topic study content generation."""
    stream_gen = svc.generate_content_stream(user, topic_id)
    return StreamingResponse(stream_gen, media_type="text/plain")


@router.get("/content/{topic_id}", response_model=TopicContentResponse,
            summary="Get generated content for a topic")
async def get_content(
    topic_id: UUID,
    user: User = Depends(get_current_user),
    svc: RoadmapService = Depends(_svc),
):
    return await svc.generate_content(user, topic_id)  # idempotent

"""
Socratic router — API endpoints for interactive Socratic AI tutoring dialogue.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents import multi_agent_orchestrator
from app.database import get_db
from app.models.user import User
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/socratic", tags=["Socratic Dialogue"])


class ChatMessage(BaseModel):
    role: str  # user | assistant
    content: str


class SocraticChatRequest(BaseModel):
    topic_title: str
    user_message: str
    history: List[ChatMessage] = []
    skill_level: str = "beginner"
    mastery_score: Optional[float] = None


class SocraticChatResponse(BaseModel):
    reply: str
    curriculum_directive: Optional[str] = None
    orchestrated_by: str


from fastapi.responses import StreamingResponse

@router.post("/chat", response_model=SocraticChatResponse)
async def socratic_chat(
    body: SocraticChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Interactive Socratic dialogue endpoint.
    Orchestrates Curriculum & Socratic agents to provide guided step-by-step responses.
    """
    history_dicts = [{"role": m.role, "content": m.content} for m in body.history]

    result = await multi_agent_orchestrator.run_socratic_dialogue(
        topic_title=body.topic_title,
        user_message=body.user_message,
        history=history_dicts,
        user_id=current_user.id,
        db_session=db,
        skill_level=body.skill_level,
        mastery_score=body.mastery_score,
    )

    return SocraticChatResponse(**result)


@router.post("/chat/stream")
async def socratic_chat_stream(
    body: SocraticChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Real-time streaming Socratic dialogue endpoint.
    Streams token chunks directly to client for instant (<1.0s) response rendering.
    """
    history_dicts = [{"role": m.role, "content": m.content} for m in body.history]

    stream_gen = multi_agent_orchestrator.socratic_agent.process_stream({
        "topic_title": body.topic_title,
        "user_message": body.user_message,
        "history": history_dicts,
        "skill_level": body.skill_level,
        "db_session": db,
        "user_id": current_user.id,
    })

    return StreamingResponse(stream_gen, media_type="text/plain")

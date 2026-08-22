"""
Pydantic schemas for roadmap endpoints.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ── Topic ──────────────────────────────────────────────────────
class TopicResponse(BaseModel):
    id: uuid.UUID
    roadmap_id: uuid.UUID
    week_number: int
    title: str
    description: Optional[str]
    order_index: int
    is_completed: bool
    created_at: datetime
    model_config = {"from_attributes": True}


class WeekGroup(BaseModel):
    week_number: int
    theme: Optional[str] = None
    topics: List[TopicResponse]


# ── Roadmap ────────────────────────────────────────────────────
class RoadmapResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    goal: str
    total_weeks: int
    status: str
    llm_model_used: Optional[str]
    created_at: datetime
    weeks: List[WeekGroup] = []
    model_config = {"from_attributes": True}


class GenerateRoadmapRequest(BaseModel):
    num_weeks: int = Field(default=8, ge=4, le=16)


# ── Content ────────────────────────────────────────────────────
class ContentResponse(BaseModel):
    id: uuid.UUID
    topic_id: uuid.UUID
    content_type: str
    body: str
    llm_model_used: Optional[str]
    generated_at: datetime
    model_config = {"from_attributes": True}


class TopicContentResponse(BaseModel):
    topic: TopicResponse
    contents: List[ContentResponse]


# ── Quiz ───────────────────────────────────────────────────────
class QuizOptionSchema(BaseModel):
    label: str
    text: str


class QuizQuestionResponse(BaseModel):
    id: uuid.UUID
    question_text: str
    question_type: str
    options: Optional[list]
    order_index: int
    # correct_answer excluded during active quiz — included in results
    model_config = {"from_attributes": True}


class QuizQuestionResultResponse(QuizQuestionResponse):
    correct_answer: str
    explanation: Optional[str]


class QuizResponse(BaseModel):
    id: uuid.UUID
    topic_id: uuid.UUID
    title: str
    total_questions: int
    pass_percentage: float
    created_at: datetime
    questions: List[QuizQuestionResponse]
    model_config = {"from_attributes": True}


class AnswerSubmit(BaseModel):
    question_id: uuid.UUID
    given_answer: str


class QuizSubmitRequest(BaseModel):
    answers: List[AnswerSubmit]
    time_taken_seconds: int = Field(default=0, ge=0)


class AttemptAnswerResult(BaseModel):
    question_id: uuid.UUID
    given_answer: Optional[str]
    is_correct: bool
    correct_answer: str
    explanation: Optional[str]


class QuizAttemptResponse(BaseModel):
    id: uuid.UUID
    quiz_id: uuid.UUID
    score: float
    percentage: float
    passed: bool
    time_taken_seconds: Optional[int]
    attempted_at: datetime
    answers: List[AttemptAnswerResult]
    model_config = {"from_attributes": True}


# ── Dashboard ──────────────────────────────────────────────────
class DashboardResponse(BaseModel):
    completed_topics: int
    total_topics: int
    completion_percentage: float
    average_quiz_score: float
    total_quiz_attempts: int
    last_activity: Optional[datetime]
    roadmap_status: Optional[str]
    roadmap_title: Optional[str]

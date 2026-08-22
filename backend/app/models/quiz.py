"""
Quiz and QuizQuestion ORM models — LLM-generated assessments per topic.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, func, JSON
from sqlalchemy.dialects.postgresql import JSONB, UUID

# ── Use JSON cross-dialects (PostgreSQL JSONB, SQLite JSON) ───────────────────
JSONType = JSON().with_variant(JSONB, "postgresql")
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Quiz(Base):
    __tablename__ = "quizzes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pass_percentage: Mapped[float] = mapped_column(Float, nullable=False, default=60.0)
    llm_model_used: Mapped[str] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Relationships ──────────────────────────────────────────
    topic: Mapped["Topic"] = relationship("Topic", back_populates="quizzes")  # noqa: F821
    questions: Mapped[list["QuizQuestion"]] = relationship(
        "QuizQuestion",
        back_populates="quiz",
        cascade="all, delete-orphan",
        order_by="QuizQuestion.order_index",
    )
    attempts: Mapped[list["QuizAttempt"]] = relationship(  # noqa: F821
        "QuizAttempt", back_populates="quiz"
    )

    def __repr__(self) -> str:
        return f"<Quiz id={self.id} title={self.title[:40]} questions={self.total_questions}>"


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    quiz_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[str] = mapped_column(
        Enum("mcq", "coding", name="question_type_enum"),
        nullable=False,
        default="mcq",
    )
    # JSON options: [{"label": "A", "text": "..."}, ...]
    options: Mapped[dict] = mapped_column(JSONType, nullable=True)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # ── Relationships ──────────────────────────────────────────
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="questions")
    answers: Mapped[list["AttemptAnswer"]] = relationship(  # noqa: F821
        "AttemptAnswer", back_populates="question"
    )

    def __repr__(self) -> str:
        return f"<QuizQuestion type={self.question_type} quiz_id={self.quiz_id}>"

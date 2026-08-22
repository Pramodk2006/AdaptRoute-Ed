"""
QuizAttempt and AttemptAnswer ORM models — records a student's quiz submission.
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quiz_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quizzes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    percentage: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    time_taken_seconds: Mapped[int] = mapped_column(
        Integer, nullable=True, comment="Time the student spent on this attempt"
    )
    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Relationships ──────────────────────────────────────────
    user: Mapped["User"] = relationship("User", back_populates="quiz_attempts")  # noqa: F821
    quiz: Mapped["Quiz"] = relationship("Quiz", back_populates="attempts")
    answers: Mapped[list["AttemptAnswer"]] = relationship(
        "AttemptAnswer", back_populates="attempt", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<QuizAttempt user={self.user_id} quiz={self.quiz_id} "
            f"score={self.percentage:.1f}% passed={self.passed}>"
        )


class AttemptAnswer(Base):
    __tablename__ = "attempt_answers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    attempt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quiz_attempts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quiz_questions.id", ondelete="CASCADE"),
        nullable=False,
    )

    given_answer: Mapped[str] = mapped_column(Text, nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # ── Relationships ──────────────────────────────────────────
    attempt: Mapped["QuizAttempt"] = relationship("QuizAttempt", back_populates="answers")
    question: Mapped["QuizQuestion"] = relationship(  # noqa: F821
        "QuizQuestion", back_populates="answers"
    )

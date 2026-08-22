"""
TopicMastery ORM model — stores Bayesian Knowledge Tracing mastery scores per topic per student.
P(L_t) ∈ [0.0, 1.0] represents the estimated probability the student has mastered this concept.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TopicMastery(Base):
    __tablename__ = "topic_masteries"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # BKT mastery probability: P(L_t)
    mastery_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.25)
    attempts_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    last_attempt_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Unique constraint: one mastery record per (user, topic)
    __table_args__ = (
        UniqueConstraint("user_id", "topic_id", name="uq_topic_mastery_user_topic"),
    )

    # ── Relationships ──────────────────────────────────────────
    user: Mapped["User"] = relationship("User")  # noqa: F821
    topic: Mapped["Topic"] = relationship("Topic")  # noqa: F821

    @property
    def mastery_level(self) -> str:
        """Human-readable mastery classification."""
        if self.mastery_score >= 0.85:
            return "mastered"
        elif self.mastery_score >= 0.70:
            return "proficient"
        elif self.mastery_score >= 0.50:
            return "developing"
        else:
            return "struggling"

    @property
    def accuracy_pct(self) -> float:
        if self.attempts_count == 0:
            return 0.0
        return round((self.correct_count / self.attempts_count) * 100, 1)

    def __repr__(self) -> str:
        return f"<TopicMastery user={self.user_id} topic={self.topic_id} P(L)={self.mastery_score:.3f}>"

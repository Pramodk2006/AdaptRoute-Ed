"""
LearnerProfile ORM model — stores student context used to personalise
roadmap generation and LLM prompts.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LearnerProfile(Base):
    __tablename__ = "learner_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    skill_level: Mapped[str] = mapped_column(
        Enum("beginner", "intermediate", "advanced", name="skill_level_enum"),
        nullable=False,
    )
    learning_goal: Mapped[str] = mapped_column(Text, nullable=False)
    preferred_pace: Mapped[str] = mapped_column(
        Enum("slow", "moderate", "fast", name="preferred_pace_enum"),
        nullable=False,
    )
    daily_study_time: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Daily study time in minutes"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ── Relationships ──────────────────────────────────────────
    user: Mapped["User"] = relationship("User", back_populates="profile")  # noqa: F821

    def __repr__(self) -> str:
        return f"<LearnerProfile user_id={self.user_id} goal={self.learning_goal[:30]}>"

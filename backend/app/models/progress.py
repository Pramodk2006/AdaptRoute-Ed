"""
Progress ORM model — aggregated learning progress per roadmap.
Updated automatically on topic completion and quiz submission.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Progress(Base):
    __tablename__ = "progress"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    roadmap_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roadmaps.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    completed_topics: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_topics: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    average_quiz_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    last_activity: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=True
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # ── Relationships ──────────────────────────────────────────
    user: Mapped["User"] = relationship("User", back_populates="progress_records")  # noqa: F821
    roadmap: Mapped["Roadmap"] = relationship("Roadmap", back_populates="progress")  # noqa: F821

    @property
    def completion_percentage(self) -> float:
        if self.total_topics == 0:
            return 0.0
        return round((self.completed_topics / self.total_topics) * 100, 1)

    def __repr__(self) -> str:
        return (
            f"<Progress user={self.user_id} "
            f"{self.completed_topics}/{self.total_topics} topics>"
        )

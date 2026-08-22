"""
Roadmap ORM model — a personalised weekly study plan tied to a user.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Roadmap(Base):
    __tablename__ = "roadmaps"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    total_weeks: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("active", "completed", "paused", name="roadmap_status_enum"),
        default="active",
        nullable=False,
    )
    llm_model_used: Mapped[str] = mapped_column(
        String(100), nullable=True, comment="LLM model that generated this roadmap"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Relationships ──────────────────────────────────────────
    user: Mapped["User"] = relationship("User", back_populates="roadmaps")  # noqa: F821
    topics: Mapped[list["Topic"]] = relationship(  # noqa: F821
        "Topic", back_populates="roadmap", cascade="all, delete-orphan",
        order_by="Topic.week_number, Topic.order_index",
    )
    progress: Mapped["Progress"] = relationship(  # noqa: F821
        "Progress", back_populates="roadmap", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Roadmap id={self.id} title={self.title[:40]} weeks={self.total_weeks}>"

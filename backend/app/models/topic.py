"""
Topic ORM model — individual learning topic within a roadmap week.
"""
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    roadmap_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roadmaps.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    week_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    order_index: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
        comment="Position within the week"
    )
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Relationships ──────────────────────────────────────────
    roadmap: Mapped["Roadmap"] = relationship("Roadmap", back_populates="topics")  # noqa: F821
    contents: Mapped[list["Content"]] = relationship(  # noqa: F821
        "Content", back_populates="topic", cascade="all, delete-orphan"
    )
    quizzes: Mapped[list["Quiz"]] = relationship(  # noqa: F821
        "Quiz", back_populates="topic", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Topic week={self.week_number} idx={self.order_index} title={self.title[:40]}>"

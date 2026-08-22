"""
Content ORM model — AI-generated study material for a topic.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Content(Base):
    __tablename__ = "contents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    topic_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    content_type: Mapped[str] = mapped_column(
        Enum("notes", "explanation", "example", name="content_type_enum"),
        nullable=False,
    )
    body: Mapped[str] = mapped_column(Text, nullable=False)
    llm_model_used: Mapped[str] = mapped_column(
        String(100), nullable=True,
        comment="Which LLM model generated this content — for routing audit"
    )
    generated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Relationships ──────────────────────────────────────────
    topic: Mapped["Topic"] = relationship("Topic", back_populates="contents")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Content type={self.content_type} topic_id={self.topic_id}>"

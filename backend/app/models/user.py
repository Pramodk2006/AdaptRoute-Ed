"""
User ORM model — core authentication entity.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
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
    profile: Mapped["LearnerProfile"] = relationship(  # noqa: F821
        "LearnerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    roadmaps: Mapped[list["Roadmap"]] = relationship(  # noqa: F821
        "Roadmap", back_populates="user", cascade="all, delete-orphan"
    )
    quiz_attempts: Mapped[list["QuizAttempt"]] = relationship(  # noqa: F821
        "QuizAttempt", back_populates="user", cascade="all, delete-orphan"
    )
    progress_records: Mapped[list["Progress"]] = relationship(  # noqa: F821
        "Progress", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"

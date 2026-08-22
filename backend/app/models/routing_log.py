"""
RoutingLog ORM model — tracks every multi-LLM routing decision, latency, cost, and reward.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, func, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RoutingLog(Base):
    __tablename__ = "routing_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    task_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    selected_model: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    routing_policy_used: Mapped[str] = mapped_column(String(50), nullable=False, default="heuristic")
    
    # Task feature metrics
    prompt_length_chars: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    user_skill_level: Mapped[str] = mapped_column(String(20), nullable=False, default="beginner")
    
    # Result metrics
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=True)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    reward_score: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="success")
    error_message: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Advanced capability/routing feedback metrics
    quality_score: Mapped[float] = mapped_column(Float, nullable=True)
    quality_passed: Mapped[bool] = mapped_column(Boolean, nullable=True)
    escalation_triggered: Mapped[bool] = mapped_column(Boolean, nullable=True)
    escalation_model: Mapped[str] = mapped_column(String(100), nullable=True)
    escalation_attempts: Mapped[int] = mapped_column(Integer, nullable=True)
    final_model: Mapped[str] = mapped_column(String(100), nullable=True)
    bandit_update_performed: Mapped[bool] = mapped_column(Boolean, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # ── Relationships ──────────────────────────────────────────
    user: Mapped["User"] = relationship("User")  # noqa: F821

    def __repr__(self) -> str:
        return f"<RoutingLog task={self.task_type} model={self.selected_model} latency={self.latency_ms}ms>"

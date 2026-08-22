"""
LinUCBState ORM model — persists model arm A-matrix and b-vector parameters
in the PostgreSQL database to preserve learning across application restarts.
"""
from datetime import datetime
from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LinUCBState(Base):
    __tablename__ = "linucb_states"

    model_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    a_matrix: Mapped[str] = mapped_column(Text, nullable=False)  # JSON-serialized floats
    b_vector: Mapped[str] = mapped_column(Text, nullable=False)  # JSON-serialized floats
    update_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<LinUCBState model={self.model_id} updates={self.update_count}>"

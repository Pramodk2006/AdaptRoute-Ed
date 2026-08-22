"""
Database engine, session factory, and base model configuration.
"""
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

# ── Engine ─────────────────────────────────────────────────────────────────────
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,          # Drop stale connections automatically
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,         # SQL logging in dev mode
)

# ── Session Factory ────────────────────────────────────────────────────────────
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ── Declarative Base ───────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """All ORM models inherit from this base."""
    pass


# ── Dependency Injection Helper ────────────────────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a database session and ensures
    it is properly closed after the request completes.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

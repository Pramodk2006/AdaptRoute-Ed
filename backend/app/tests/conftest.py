"""
Pytest configuration and shared fixtures for AdaptRoute-Edu backend tests.
Uses an in-memory SQLite database for isolated, fast, reproducible testing.
"""
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.database import get_db, Base
from app.main import app
from app.models.user import User
from app.models.learner_profile import LearnerProfile
from app.utils.security import hash_password, create_access_token

# ── In-Memory SQLite Setup ───────────────────────────────────────────────────
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Create all database tables in memory before running tests."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Provide a transactional database session that rolls back after each test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient with overridden get_db dependency."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a verified test user in the database."""
    user = User(
        email="teststudent@example.com",
        username="teststudent",
        hashed_password=hash_password("Password123"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Provide Bearer authorization headers for the test user."""
    token = create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def test_profile(db_session: Session, test_user: User) -> LearnerProfile:
    """Create a test learner profile for test_user."""
    profile = LearnerProfile(
        user_id=test_user.id,
        full_name="Test Student",
        skill_level="intermediate",
        learning_goal="Master Python data science and machine learning",
        preferred_pace="moderate",
        daily_study_time=60,
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile

"""
UserRepository — all database operations involving the User model.
Services must not call db.query(User) directly; use this repository instead.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Read ───────────────────────────────────────────────────────────────────

    def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(User.email == email.lower().strip())
            .first()
        )

    def get_by_username(self, username: str) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(User.username == username)
            .first()
        )

    def email_exists(self, email: str) -> bool:
        return self.get_by_email(email) is not None

    def username_exists(self, username: str) -> bool:
        return self.get_by_username(username) is not None

    # ── Write ──────────────────────────────────────────────────────────────────

    def create(self, email: str, username: str, hashed_password: str) -> User:
        user = User(
            email=email.lower().strip(),
            username=username,
            hashed_password=hashed_password,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def deactivate(self, user: User) -> User:
        user.is_active = False
        self.db.commit()
        self.db.refresh(user)
        return user

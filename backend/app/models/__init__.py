"""
models package — imports all models so Alembic can discover them.
All ORM models must be imported here before alembic autogenerate runs.
"""
from app.models.user import User
from app.models.learner_profile import LearnerProfile
from app.models.roadmap import Roadmap
from app.models.topic import Topic
from app.models.content import Content
from app.models.quiz import Quiz, QuizQuestion
from app.models.quiz_attempt import QuizAttempt, AttemptAnswer
from app.models.progress import Progress
from app.models.routing_log import RoutingLog
from app.models.topic_mastery import TopicMastery
from app.models.linucb_state import LinUCBState

__all__ = [
    "User",
    "LearnerProfile",
    "Roadmap",
    "Topic",
    "Content",
    "Quiz",
    "QuizQuestion",
    "QuizAttempt",
    "AttemptAnswer",
    "Progress",
    "RoutingLog",
    "TopicMastery",
    "LinUCBState",
]

"""
RoadmapRepository — DB operations for Roadmap, Topic, Content, Progress.
"""
import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.roadmap import Roadmap
from app.models.topic import Topic
from app.models.content import Content
from app.models.progress import Progress


class RoadmapRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Roadmap ────────────────────────────────────────────────
    def get_active_roadmap(self, user_id: uuid.UUID) -> Optional[Roadmap]:
        return (
            self.db.query(Roadmap)
            .filter(Roadmap.user_id == user_id, Roadmap.status == "active")
            .order_by(Roadmap.created_at.desc())
            .first()
        )

    def deactivate_old_roadmaps(self, user_id: uuid.UUID) -> None:
        self.db.query(Roadmap).filter(
            Roadmap.user_id == user_id, Roadmap.status == "active"
        ).update({"status": "paused"})

    def get_roadmap_by_id(self, roadmap_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Roadmap]:
        return (
            self.db.query(Roadmap)
            .filter(Roadmap.id == roadmap_id, Roadmap.user_id == user_id)
            .first()
        )

    def create_roadmap(
        self,
        user_id: uuid.UUID,
        title: str,
        goal: str,
        total_weeks: int,
        llm_model: str,
    ) -> Roadmap:
        roadmap = Roadmap(
            user_id=user_id,
            title=title,
            goal=goal,
            total_weeks=total_weeks,
            status="active",
            llm_model_used=llm_model,
        )
        self.db.add(roadmap)
        self.db.flush()  # get roadmap.id without full commit
        return roadmap

    # ── Topics ─────────────────────────────────────────────────
    def bulk_create_topics(self, topics_data: List[dict]) -> List[Topic]:
        topics = [Topic(**data) for data in topics_data]
        self.db.add_all(topics)
        return topics

    def get_topic(self, topic_id: uuid.UUID) -> Optional[Topic]:
        return self.db.get(Topic, topic_id)

    def mark_topic_complete(self, topic: Topic) -> Topic:
        topic.is_completed = True
        self.db.commit()
        self.db.refresh(topic)
        return topic

    def get_topics_for_roadmap(self, roadmap_id: uuid.UUID) -> List[Topic]:
        return (
            self.db.query(Topic)
            .filter(Topic.roadmap_id == roadmap_id)
            .order_by(Topic.week_number, Topic.order_index)
            .all()
        )

    # ── Content ────────────────────────────────────────────────
    def get_content_for_topic(self, topic_id: uuid.UUID) -> List[Content]:
        return (
            self.db.query(Content)
            .filter(Content.topic_id == topic_id)
            .all()
        )

    def create_contents(self, contents_data: List[dict]) -> List[Content]:
        contents = [Content(**data) for data in contents_data]
        self.db.add_all(contents)
        self.db.commit()
        return contents

    # ── Progress ───────────────────────────────────────────────
    def get_or_create_progress(
        self, user_id: uuid.UUID, roadmap_id: uuid.UUID, total_topics: int
    ) -> Progress:
        progress = (
            self.db.query(Progress)
            .filter(Progress.roadmap_id == roadmap_id)
            .first()
        )
        if not progress:
            progress = Progress(
                user_id=user_id,
                roadmap_id=roadmap_id,
                total_topics=total_topics,
                completed_topics=0,
                average_quiz_score=0.0,
            )
            self.db.add(progress)
            self.db.commit()
            self.db.refresh(progress)
        return progress

    def update_progress_on_topic_complete(self, roadmap_id: uuid.UUID) -> None:
        progress = (
            self.db.query(Progress)
            .filter(Progress.roadmap_id == roadmap_id)
            .first()
        )
        if progress:
            completed = (
                self.db.query(Topic)
                .filter(Topic.roadmap_id == roadmap_id, Topic.is_completed == True)
                .count()
            )
            progress.completed_topics = completed
            from datetime import datetime, timezone
            progress.last_activity = datetime.now(timezone.utc)
            self.db.commit()

    def update_progress_quiz_score(
        self, user_id: uuid.UUID, roadmap_id: uuid.UUID, new_score: float
    ) -> None:
        from sqlalchemy import func
        from app.models.quiz_attempt import QuizAttempt

        avg = (
            self.db.query(func.avg(QuizAttempt.percentage))
            .filter(QuizAttempt.user_id == user_id)
            .scalar()
        ) or 0.0

        progress = (
            self.db.query(Progress)
            .filter(Progress.roadmap_id == roadmap_id)
            .first()
        )
        if progress:
            progress.average_quiz_score = round(float(avg), 2)
            self.db.commit()

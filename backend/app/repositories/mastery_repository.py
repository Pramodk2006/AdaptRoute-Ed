"""
Mastery repository — CRUD and aggregation for TopicMastery records.
"""
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.knowledge.bkt_engine import batch_update_mastery, DEFAULT_PARAMS
from app.models.topic_mastery import TopicMastery


class MasteryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create(self, user_id: uuid.UUID, topic_id: uuid.UUID) -> TopicMastery:
        """Fetch existing mastery record or create a new one with prior P(L_0)."""
        stmt = select(TopicMastery).where(
            TopicMastery.user_id == user_id,
            TopicMastery.topic_id == topic_id,
        )
        record = self.db.scalar(stmt)
        if record is None:
            record = TopicMastery(
                user_id=user_id,
                topic_id=topic_id,
                mastery_score=DEFAULT_PARAMS.p_init,
                attempts_count=0,
                correct_count=0,
            )
            self.db.add(record)
            self.db.flush()
        return record

    def update_after_quiz(
        self,
        user_id: uuid.UUID,
        topic_id: uuid.UUID,
        correct_count: int,
        total_questions: int,
    ) -> TopicMastery:
        """
        Apply BKT update to topic mastery after a quiz attempt.
        Returns the updated TopicMastery record.
        """
        record = self.get_or_create(user_id, topic_id)

        new_mastery = batch_update_mastery(
            current_mastery=record.mastery_score,
            correct_count=correct_count,
            total_count=total_questions,
        )

        record.mastery_score = new_mastery
        record.attempts_count += total_questions
        record.correct_count += correct_count
        record.last_attempt_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_user_mastery(self, user_id: uuid.UUID) -> List[TopicMastery]:
        """Fetch all topic mastery records for a student."""
        stmt = select(TopicMastery).where(TopicMastery.user_id == user_id)
        return list(self.db.scalars(stmt).all())

    def get_topic_mastery(
        self, user_id: uuid.UUID, topic_id: uuid.UUID
    ) -> Optional[TopicMastery]:
        """Fetch mastery for a specific topic."""
        stmt = select(TopicMastery).where(
            TopicMastery.user_id == user_id,
            TopicMastery.topic_id == topic_id,
        )
        return self.db.scalar(stmt)

    def get_mastery_stats(self, user_id: uuid.UUID) -> Dict:
        """Compute aggregate mastery statistics across all topics."""
        records = self.get_user_mastery(user_id)
        if not records:
            return {
                "topics_tracked": 0,
                "avg_mastery": 0.0,
                "mastered_count": 0,
                "proficient_count": 0,
                "developing_count": 0,
                "struggling_count": 0,
                "overall_readiness": 0.0,
            }

        total = len(records)
        avg = sum(r.mastery_score for r in records) / total
        levels = {"mastered": 0, "proficient": 0, "developing": 0, "struggling": 0}
        for r in records:
            levels[r.mastery_level] += 1

        readiness = round(
            (levels["mastered"] * 1.0 + levels["proficient"] * 0.8) / total * 100, 1
        )

        return {
            "topics_tracked": total,
            "avg_mastery": round(avg, 3),
            "mastered_count": levels["mastered"],
            "proficient_count": levels["proficient"],
            "developing_count": levels["developing"],
            "struggling_count": levels["struggling"],
            "overall_readiness": readiness,
        }

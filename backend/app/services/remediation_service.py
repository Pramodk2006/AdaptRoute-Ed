"""
Adaptive Remediation Service — generates targeted diagnostic study notes when
student mastery is below threshold.
Uses the Multi-LLM Router to select the optimal model for remediation generation.
"""
import uuid
from typing import List, Optional
from sqlalchemy.orm import Session

from app.knowledge.bkt_engine import needs_remediation
from app.llm.factory import get_provider
from app.repositories.mastery_repository import MasteryRepository
from app.repositories.routing_repository import RoutingRepository
from app.router import router_engine
from app.utils.logger import logger


class RemediationService:
    def __init__(self, db: Session):
        self.db = db
        self.mastery_repo = MasteryRepository(db)
        self.routing_repo = RoutingRepository(db)

    async def generate_remediation_notes(
        self,
        user_id: uuid.UUID,
        topic_id: uuid.UUID,
        topic_title: str,
        skill_level: str,
        missed_concepts: List[str],
    ) -> str:
        """
        Generate targeted diagnostic review notes for a struggling student.

        Args:
            user_id: Student UUID.
            topic_id: Topic UUID that requires remediation.
            topic_title: Human-readable topic name.
            skill_level: Student's skill level (beginner/intermediate/advanced).
            missed_concepts: List of concepts the student answered incorrectly.

        Returns:
            Markdown-formatted remediation notes string.
        """
        mastery = self.mastery_repo.get_topic_mastery(user_id, topic_id)
        mastery_score = mastery.mastery_score if mastery else 0.25

        missed_str = "\n".join(f"- {c}" for c in missed_concepts) if missed_concepts else "- General review required"

        prompt = f"""You are an expert adaptive tutor. A {skill_level} student is struggling with the topic: "{topic_title}".

Their estimated knowledge mastery score is {mastery_score:.2f} (0=no knowledge, 1=full mastery).

The following concepts were answered INCORRECTLY and need remediation:
{missed_str}

Generate a focused, concise remediation study note (300-500 words) that:
1. Clearly re-explains each missed concept in simple terms
2. Uses an analogy or real-world example for each concept
3. Provides a small worked example where relevant
4. Ends with 2-3 key takeaways to remember

Respond in clear Markdown format. Do NOT include quiz questions. Focus only on re-teaching the missed concepts."""

        # Route via Adaptive Router - remediation is an explanation task
        import time
        from app.services.adaptive_llm_service import AdaptiveLLMService
        try:
            response = await AdaptiveLLMService.generate(
                db_session=self.db,
                user_id=user_id,
                task_type="explanation",
                prompt=prompt,
                user_skill_level=skill_level,
                max_tokens=1024,
            )
            return response.text

        except Exception as e:
            logger.error(f"Remediation generation failed for topic {topic_id}: {e}")
            raise

    def check_remediation_needed(
        self,
        user_id: uuid.UUID,
        topic_id: uuid.UUID,
        quiz_score_pct: float,
    ) -> bool:
        """Check if a student needs remediation after a quiz attempt."""
        mastery = self.mastery_repo.get_topic_mastery(user_id, topic_id)
        mastery_score = mastery.mastery_score if mastery else 0.25
        return needs_remediation(mastery_score, quiz_score_pct)

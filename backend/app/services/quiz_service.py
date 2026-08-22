"""QuizService — LLM quiz generation and attempt evaluation."""
import json
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.llm.factory import get_provider
from app.models.user import User
from app.prompts.quiz_prompt import build_quiz_prompt
from app.services.quiz_generator import generate_tailored_quiz
from app.repositories.mastery_repository import MasteryRepository
from app.repositories.quiz_repository import QuizRepository
from app.repositories.roadmap_repository import RoadmapRepository
from app.repositories.profile_repository import ProfileRepository
from app.schemas.roadmap import (
    QuizResponse, QuizQuestionResponse, QuizSubmitRequest,
    QuizAttemptResponse, AttemptAnswerResult,
)
from app.utils.logger import logger


class QuizService:
    def __init__(
        self,
        quiz_repo: QuizRepository,
        roadmap_repo: RoadmapRepository,
        profile_repo: ProfileRepository,
        db: Session | None = None,
    ) -> None:
        self.quiz_repo = quiz_repo
        self.roadmap_repo = roadmap_repo
        self.profile_repo = profile_repo
        self.db = db

    async def generate_quiz(self, user: User, topic_id: UUID) -> QuizResponse:
        topic = self.roadmap_repo.get_topic(topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found.")

        roadmap = self.roadmap_repo.get_roadmap_by_id(topic.roadmap_id, user.id)
        if not roadmap:
            raise HTTPException(status_code=403, detail="Access denied.")

        # Return cached quiz if exists
        existing = self.quiz_repo.get_quiz_for_topic(topic_id)
        if existing:
            return self._build_quiz_response(existing)

        profile = self.profile_repo.get_by_user_id(user.id)
        prompt = build_quiz_prompt(
            topic_title=topic.title,
            topic_description=topic.description or "",
            skill_level=profile.skill_level if profile else "beginner",
            num_questions=5,
        )

        from app.services.adaptive_llm_service import AdaptiveLLMService
        try:
            response = await AdaptiveLLMService.generate(
                db_session=self.db,
                user_id=user.id,
                task_type="quiz",
                prompt=prompt,
                user_skill_level=profile.skill_level if profile else "beginner",
                preferred_pace=profile.preferred_pace if profile else "moderate",
                daily_study_time=profile.daily_study_time if profile else 60,
                is_json=True,
                max_tokens=600,
            )
            raw = response.text
            data = self._parse_json(raw)
            provider_name = response.model
        except Exception as e:
            logger.warning(f"LLM quiz generation warning: {e}, using domain-tailored quiz generator")
            data = generate_tailored_quiz(topic.title, profile.skill_level if profile else "beginner")
            provider_name = "tailored-quiz-engine"

        if not data.get("questions"):
            data = generate_tailored_quiz(topic.title, profile.skill_level if profile else "beginner")
            provider_name = "tailored-quiz-engine"

        quiz = self.quiz_repo.create_quiz(
            topic_id=topic_id,
            title=data.get("title", f"Diagnostic Assessment: {topic.title}"),
            questions_data=data.get("questions", []),
            llm_model=provider_name,
        )
        return self._build_quiz_response(quiz)

    def get_quiz(self, user: User, topic_id: UUID) -> QuizResponse:
        topic = self.roadmap_repo.get_topic(topic_id)
        if not topic:
            raise HTTPException(status_code=404, detail="Topic not found.")
        quiz = self.quiz_repo.get_quiz_for_topic(topic_id)
        if not quiz:
            # Auto-generate diagnostic quiz on first GET call (< 10ms)
            profile = self.profile_repo.get_by_user_id(user.id)
            data = generate_tailored_quiz(topic.title, profile.skill_level if profile else "beginner")
            quiz = self.quiz_repo.create_quiz(
                topic_id=topic_id,
                title=data.get("title", f"Diagnostic Assessment: {topic.title}"),
                questions_data=data.get("questions", []),
                llm_model="tailored-quiz-engine",
            )
        return self._build_quiz_response(quiz)

    def submit_quiz(
        self, user: User, quiz_id: UUID, payload: QuizSubmitRequest
    ) -> QuizAttemptResponse:
        quiz = self.quiz_repo.get_quiz_by_id(quiz_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found.")

        # Build answer evaluation
        evaluated = []
        for ans in payload.answers:
            question = self.quiz_repo.get_question(ans.question_id)
            if not question or question.quiz_id != quiz_id:
                continue
            given = (ans.given_answer or "").strip().upper()
            correct = (question.correct_answer or "").strip().upper()
            is_correct = bool(given and given == correct)
            evaluated.append({
                "question_id": ans.question_id,
                "given_answer": ans.given_answer,
                "is_correct": is_correct,
                "correct_answer": question.correct_answer,
                "explanation": question.explanation,
            })

        attempt = self.quiz_repo.create_attempt(
            user_id=user.id,
            quiz=quiz,
            answers=evaluated,
            time_taken_seconds=payload.time_taken_seconds,
        )

        # Update progress average score
        topic = self.roadmap_repo.get_topic(quiz.topic_id)
        if topic:
            self.roadmap_repo.update_progress_quiz_score(
                user_id=user.id,
                roadmap_id=topic.roadmap_id,
                new_score=attempt.percentage,
            )

        # ── BKT Knowledge Tracing update ─────────────────────
        if self.db and topic:
            correct_count = sum(1 for a in evaluated if a["is_correct"])
            total_questions = len(evaluated)
            mastery_repo = MasteryRepository(self.db)
            mastery_repo.update_after_quiz(
                user_id=user.id,
                topic_id=quiz.topic_id,
                correct_count=correct_count,
                total_questions=total_questions,
            )
            logger.info(
                f"BKT updated: user={user.id} topic={quiz.topic_id} "
                f"correct={correct_count}/{total_questions}"
            )

        return QuizAttemptResponse(
            id=attempt.id,
            quiz_id=attempt.quiz_id,
            score=attempt.score,
            percentage=attempt.percentage,
            passed=attempt.passed,
            time_taken_seconds=attempt.time_taken_seconds,
            attempted_at=attempt.attempted_at,
            answers=[
                AttemptAnswerResult(
                    question_id=a["question_id"],
                    given_answer=a.get("given_answer"),
                    is_correct=a["is_correct"],
                    correct_answer=a["correct_answer"],
                    explanation=a.get("explanation"),
                )
                for a in evaluated
            ],
        )

    def get_attempt(self, user: User, attempt_id: UUID) -> QuizAttemptResponse:
        attempt = self.quiz_repo.get_attempt_by_id(attempt_id, user.id)
        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt not found.")
        return QuizAttemptResponse(
            id=attempt.id,
            quiz_id=attempt.quiz_id,
            score=attempt.score,
            percentage=attempt.percentage,
            passed=attempt.passed,
            time_taken_seconds=attempt.time_taken_seconds,
            attempted_at=attempt.attempted_at,
            answers=[
                AttemptAnswerResult(
                    question_id=a.question_id,
                    given_answer=a.given_answer,
                    is_correct=a.is_correct,
                    correct_answer=a.question.correct_answer,
                    explanation=a.question.explanation,
                )
                for a in attempt.answers
            ],
        )

    def _build_quiz_response(self, quiz) -> QuizResponse:
        return QuizResponse(
            id=quiz.id,
            topic_id=quiz.topic_id,
            title=quiz.title,
            total_questions=quiz.total_questions,
            pass_percentage=quiz.pass_percentage,
            created_at=quiz.created_at,
            questions=[QuizQuestionResponse.model_validate(q) for q in quiz.questions],
        )

    def _parse_json(self, raw: str) -> dict:
        text = raw.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            logger.error(f"Quiz JSON parse error: {exc} | raw: {raw[:200]}")
            raise HTTPException(status_code=502, detail="LLM returned invalid quiz JSON. Please retry.")

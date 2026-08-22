"""Quiz repository — DB operations for Quiz, QuizAttempt, AttemptAnswer."""
import uuid
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.quiz import Quiz, QuizQuestion
from app.models.quiz_attempt import QuizAttempt, AttemptAnswer


class QuizRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_quiz_for_topic(self, topic_id: uuid.UUID) -> Optional[Quiz]:
        return (
            self.db.query(Quiz)
            .filter(Quiz.topic_id == topic_id)
            .order_by(Quiz.created_at.desc())
            .first()
        )

    def get_quiz_by_id(self, quiz_id: uuid.UUID | str) -> Optional[Quiz]:
        try:
            q_uuid = uuid.UUID(str(quiz_id))
            return self.db.get(Quiz, q_uuid)
        except Exception:
            return None

    def get_question(self, question_id: uuid.UUID | str) -> Optional[QuizQuestion]:
        try:
            q_uuid = uuid.UUID(str(question_id))
            return self.db.get(QuizQuestion, q_uuid)
        except Exception:
            return None

    def create_quiz(
        self,
        topic_id: uuid.UUID,
        title: str,
        questions_data: List[dict],
        llm_model: str,
        pass_percentage: float = 60.0,
    ) -> Quiz:
        quiz = Quiz(
            topic_id=topic_id,
            title=title,
            total_questions=len(questions_data),
            pass_percentage=pass_percentage,
            llm_model_used=llm_model,
        )
        self.db.add(quiz)
        self.db.flush()

        for q_data in questions_data:
            question = QuizQuestion(
                quiz_id=quiz.id,
                question_text=q_data["question_text"],
                question_type=q_data.get("question_type", "mcq"),
                options=q_data.get("options"),
                correct_answer=q_data["correct_answer"],
                explanation=q_data.get("explanation"),
                order_index=q_data.get("order_index", 0),
            )
            self.db.add(question)

        self.db.commit()
        self.db.refresh(quiz)
        return quiz

    def create_attempt(
        self,
        user_id: uuid.UUID,
        quiz: Quiz,
        answers: List[dict],
        time_taken_seconds: int,
    ) -> QuizAttempt:
        correct = sum(1 for a in answers if a["is_correct"])
        total = quiz.total_questions
        percentage = round((correct / total) * 100, 2) if total > 0 else 0.0
        passed = percentage >= quiz.pass_percentage

        attempt = QuizAttempt(
            user_id=user_id,
            quiz_id=quiz.id,
            score=float(correct),
            percentage=percentage,
            passed=passed,
            time_taken_seconds=time_taken_seconds,
        )
        self.db.add(attempt)
        self.db.flush()

        for a in answers:
            self.db.add(AttemptAnswer(
                attempt_id=attempt.id,
                question_id=a["question_id"],
                given_answer=a.get("given_answer"),
                is_correct=a["is_correct"],
            ))

        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    def get_attempts_for_user(self, user_id: uuid.UUID) -> List[QuizAttempt]:
        return (
            self.db.query(QuizAttempt)
            .filter(QuizAttempt.user_id == user_id)
            .order_by(QuizAttempt.attempted_at.desc())
            .all()
        )

    def get_attempt_by_id(self, attempt_id: uuid.UUID, user_id: uuid.UUID) -> Optional[QuizAttempt]:
        return (
            self.db.query(QuizAttempt)
            .filter(QuizAttempt.id == attempt_id, QuizAttempt.user_id == user_id)
            .first()
        )

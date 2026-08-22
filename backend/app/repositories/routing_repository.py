"""
Routing repository — data access for RoutingLog table.
"""
import uuid
from typing import Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.routing_log import RoutingLog


class RoutingRepository:
    def __init__(self, db: Session):
        self.db = db

    def log_decision(
        self,
        user_id: uuid.UUID,
        task_type: str,
        selected_model: str,
        routing_policy_used: str,
        prompt_length_chars: int,
        user_skill_level: str,
        latency_ms: Optional[int] = None,
        prompt_tokens: Optional[int] = None,
        completion_tokens: Optional[int] = None,
        estimated_cost_usd: float = 0.0,
        reward_score: Optional[float] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        quality_score: Optional[float] = None,
        quality_passed: Optional[bool] = None,
        escalation_triggered: Optional[bool] = None,
        escalation_model: Optional[str] = None,
        escalation_attempts: Optional[int] = None,
        final_model: Optional[str] = None,
        bandit_update_performed: Optional[bool] = None,
    ) -> RoutingLog:
        """Create and persist a new routing log entry."""
        log = RoutingLog(
            user_id=user_id,
            task_type=task_type,
            selected_model=selected_model,
            routing_policy_used=routing_policy_used,
            prompt_length_chars=prompt_length_chars,
            user_skill_level=user_skill_level,
            latency_ms=latency_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            estimated_cost_usd=estimated_cost_usd,
            reward_score=reward_score,
            status=status,
            error_message=error_message,
            quality_score=quality_score,
            quality_passed=quality_passed,
            escalation_triggered=escalation_triggered,
            escalation_model=escalation_model,
            escalation_attempts=escalation_attempts,
            final_model=final_model,
            bandit_update_performed=bandit_update_performed,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def get_user_logs(self, user_id: uuid.UUID, limit: int = 50) -> List[RoutingLog]:
        """Fetch recent routing decision logs for a user."""
        stmt = (
            select(RoutingLog)
            .where(RoutingLog.user_id == user_id)
            .order_by(RoutingLog.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def get_telemetry_stats(self, user_id: Optional[uuid.UUID] = None) -> Dict:
        """Calculate aggregated telemetry metrics across models and policies."""
        query = select(RoutingLog)
        if user_id:
            query = query.where(RoutingLog.user_id == user_id)

        logs = list(self.db.scalars(query).all())
        total_requests = len(logs)

        if total_requests == 0:
            return {
                "total_requests": 0,
                "model_distribution": {},
                "avg_latency_ms": 0,
                "total_estimated_cost_usd": 0.0,
                "avg_reward_score": 0.0,
                "recent_logs": [],
            }

        # Model distribution
        model_counts: Dict[str, int] = {}
        total_latency = 0
        total_cost = 0.0
        total_reward = 0.0
        valid_reward_count = 0

        for log in logs:
            model_counts[log.selected_model] = model_counts.get(log.selected_model, 0) + 1
            if log.latency_ms:
                total_latency += log.latency_ms
            if log.estimated_cost_usd:
                total_cost += log.estimated_cost_usd
            if log.reward_score is not None:
                total_reward += log.reward_score
                valid_reward_count += 1

        model_dist = {
            m: round((c / total_requests) * 100, 1) for m, c in model_counts.items()
        }

        return {
            "total_requests": total_requests,
            "model_distribution": model_dist,
            "avg_latency_ms": round(total_latency / total_requests) if total_requests else 0,
            "total_estimated_cost_usd": round(total_cost, 6),
            "avg_reward_score": round(total_reward / valid_reward_count, 3) if valid_reward_count else 0.0,
            "recent_logs": [
                {
                    "id": str(l.id),
                    "task_type": l.task_type,
                    "selected_model": l.selected_model,
                    "routing_policy": l.routing_policy_used,
                    "latency_ms": l.latency_ms,
                    "reward_score": l.reward_score,
                    "created_at": l.created_at.isoformat(),
                }
                for l in logs[:10]
            ],
        }

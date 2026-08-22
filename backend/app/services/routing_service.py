"""
Routing service — business logic for policy switching, telemetry retrieval, and manual router configuration.
"""
import uuid
from typing import Dict
from sqlalchemy.orm import Session

from app.repositories.routing_repository import RoutingRepository
from app.router import router_engine
from app.router.registry import MODEL_REGISTRY


class RoutingService:
    def __init__(self, db: Session):
        self.repo = RoutingRepository(db)

    def get_telemetry(self, user_id: uuid.UUID) -> Dict:
        """Fetch router telemetry metrics and available models."""
        stats = self.repo.get_telemetry_stats(user_id=user_id)
        stats["active_policy"] = router_engine.active_policy_name
        stats["available_models"] = [
            {
                "model_id": m.model_id,
                "display_name": m.display_name,
                "tier": m.tier,
                "reasoning_score": m.capabilities.reasoning,
                "code_score": m.capabilities.coding,
                "knowledge_score": m.capabilities.knowledge,
                "speed_score": m.capabilities.speed_score,
            }
            for m in MODEL_REGISTRY.values()
        ]
        return stats

    def set_policy(self, policy_name: str) -> Dict:
        """Change the active router policy mode ('heuristic' | 'bandit')."""
        if policy_name not in ("heuristic", "bandit"):
            raise ValueError("Policy must be either 'heuristic' or 'bandit'.")

        router_engine.active_policy_name = policy_name
        return {"status": "success", "active_policy": policy_name}

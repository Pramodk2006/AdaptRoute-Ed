"""
Routing Policies:
  - CapabilityFilter        — eliminates models incapable of satisfying task requirements
  - HeuristicRouterPolicy   — score-based deterministic selection from filtered candidates
  - BanditRouterPolicy      — LinUCB contextual bandit on filtered candidates (9D feature vector)
"""
import random
from typing import Dict, List, Tuple

import numpy as np

from app.router.feature_extractor import TaskFeatures
from app.router.registry import MODEL_REGISTRY, ModelProfile, get_model_profile


# ── Capability matching weights (must sum to 1.0) ────────────────────────────
_CAPABILITY_WEIGHTS = {
    "reasoning":        0.18,
    "coding":           0.14,
    "knowledge":        0.18,
    "long_generation":  0.15,
    "context":          0.10,
    "structured_output": 0.13,
    "accuracy":         0.12,
}


def _capability_match_score(profile: ModelProfile, features: TaskFeatures) -> float:
    """
    Compute a 0.0–1.0 score measuring how well a model's capabilities
    satisfy the task's requirements.

    For each dimension we compute: min(model_capability / requirement, 1.0)
    so a model that *exceeds* a requirement doesn't get infinite credit,
    but a model that falls short is penalised proportionally.
    """
    c = profile.capabilities
    reqs = {
        "reasoning":         features.reasoning_requirement,
        "coding":            features.coding_requirement,
        "knowledge":         features.knowledge_requirement,
        "long_generation":   features.output_length_requirement,
        "context":           features.context_requirement,
        "structured_output": features.structured_output_requirement,
        "accuracy":          features.accuracy_requirement,
    }
    model_caps = {
        "reasoning":         c.reasoning,
        "coding":            c.coding,
        "knowledge":         c.knowledge,
        "long_generation":   c.long_generation,
        "context":           c.long_context,
        "structured_output": c.structured_output,
        "accuracy":          c.accuracy,
    }

    total = 0.0
    for dim, weight in _CAPABILITY_WEIGHTS.items():
        req = reqs[dim]
        if req < 0.05:
            # Near-zero requirement — full score regardless
            total += weight
        else:
            ratio = min(model_caps[dim] / req, 1.0)
            total += weight * ratio

    return round(total, 4)


class CapabilityFilter:
    """
    Stage-1 router: eliminates models whose capability match score falls
    below the required threshold.  Always returns ≥1 candidate (graceful
    fallback to best available if all fail the threshold).
    """

    def __init__(self, threshold: float = 0.70):
        self.threshold = threshold

    def filter_capable_models(
        self,
        features: TaskFeatures,
        available_models: List[str],
    ) -> List[Tuple[str, float]]:
        """
        Returns a list of (model_id, match_score) tuples for models that meet
        the capability threshold, sorted by match_score descending.

        Falls back to the single best-matching model if none reach threshold.
        """
        scored: List[Tuple[str, float]] = []
        for model_id in available_models:
            profile = get_model_profile(model_id)
            score = _capability_match_score(profile, features)
            scored.append((model_id, score))

        scored.sort(key=lambda x: x[1], reverse=True)

        capable = [(m, s) for m, s in scored if s >= self.threshold]
        if capable:
            return capable

        # Graceful fallback — return best single match so routing never fails
        return scored[:1]


class BaseRoutingPolicy:
    """Abstract routing policy interface."""

    def select_model(
        self,
        features: TaskFeatures,
        candidates: List[Tuple[str, float]],   # (model_id, match_score)
    ) -> str:
        raise NotImplementedError

    def update_reward(
        self, model_id: str, features: TaskFeatures, reward: float
    ) -> None:
        pass


class HeuristicRouterPolicy(BaseRoutingPolicy):
    """
    Score-based deterministic policy.

    Final score = capability_match × 0.60 + speed_score × 0.25 – cost_score × 0.15

    Works entirely on the pre-filtered candidate list — never sees incapable models.
    """

    def select_model(
        self,
        features: TaskFeatures,
        candidates: List[Tuple[str, float]],
    ) -> str:
        if not candidates:
            return "gemma3:latest"

        best_model = candidates[0][0]
        best_score = -float("inf")

        for model_id, match_score in candidates:
            profile = get_model_profile(model_id)
            speed = profile.capabilities.speed_score
            cost = profile.cost_per_1k_output * 100.0  # normalise to ~0–0.3 range

            final = match_score * 0.60 + speed * 0.25 - min(cost, 0.15)
            if final > best_score:
                best_score = final
                best_model = model_id

        return best_model


class BanditRouterPolicy(BaseRoutingPolicy):
    """
    Contextual Multi-Armed Bandit (LinUCB with ε-greedy exploration).

    Operates ONLY on the capability-filtered candidate list.
    Feature dimension is 9 to match TaskFeatures.to_vector().
    """

    FEATURE_DIM = 9

    def __init__(self, alpha: float = 0.5, epsilon: float = 0.10):
        self.alpha = alpha
        self.epsilon = epsilon
        self.A: Dict[str, np.ndarray] = {}
        self.b: Dict[str, np.ndarray] = {}

    def set_arm_state(self, model_id: str, A: np.ndarray, b: np.ndarray) -> None:
        """Explicitly override A and b for a model arm (e.g. loading from database)."""
        self.A[model_id] = A
        self.b[model_id] = b

    def _init_arm(self, model_id: str) -> None:
        if model_id not in self.A:
            self.A[model_id] = np.identity(self.FEATURE_DIM)
            self.b[model_id] = np.zeros((self.FEATURE_DIM, 1))

    def select_model(
        self,
        features: TaskFeatures,
        candidates: List[Tuple[str, float]],
    ) -> str:
        if not candidates:
            return "gemma3:latest"

        candidate_ids = [m for m, _ in candidates]

        # ε-greedy exploration
        if random.random() < self.epsilon:
            return random.choice(candidate_ids)

        context = np.array(features.to_vector()).reshape(-1, 1)
        best_model = candidate_ids[0]
        max_ucb = -float("inf")

        for model_id in candidate_ids:
            self._init_arm(model_id)
            A_inv = np.linalg.inv(self.A[model_id])
            theta = A_inv @ self.b[model_id]
            # UCB score: expected reward + exploration bonus
            ucb = float((theta.T @ context)[0, 0]) + self.alpha * float(
                np.sqrt((context.T @ A_inv @ context)[0, 0])
            )
            if ucb > max_ucb:
                max_ucb = ucb
                best_model = model_id

        return best_model

    def update_reward(
        self, model_id: str, features: TaskFeatures, reward: float
    ) -> None:
        """Online parameter update (Sherman-Morrison-style rank-1 update)."""
        self._init_arm(model_id)
        context = np.array(features.to_vector()).reshape(-1, 1)
        self.A[model_id] += context @ context.T
        self.b[model_id] += reward * context

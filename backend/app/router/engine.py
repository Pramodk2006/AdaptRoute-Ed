"""
Adaptive Router Engine — three-stage pipeline:
  1. Feature Extraction  (what does this task NEED?)
  2. Capability Filter   (which models CAN satisfy it?)
  3. Policy Selection    (which capable model is BEST right now?)

Plus task-dependent reward computation and quality-based escalation.
"""
from typing import Dict, List, Optional, Tuple

from app.config import get_settings
from app.router.evaluator import QualityReport, evaluate_response
from app.router.feature_extractor import TaskFeatures, extract_features
from app.router.policies import (
    BaseRoutingPolicy,
    BanditRouterPolicy,
    CapabilityFilter,
    HeuristicRouterPolicy,
)
from app.router.registry import MODEL_REGISTRY, ModelProfile, get_model_profile
from app.utils.logger import logger

settings = get_settings()


# ── Task-dependent reward weights ─────────────────────────────────────────────
_REWARD_WEIGHTS: Dict[str, Dict[str, float]] = {
    "roadmap": {
        "quality":  0.60,
        "latency":  0.10,
        "cost":     0.10,
        "success":  0.20,
    },
    "quiz": {
        "quality":  0.50,
        "latency":  0.10,
        "cost":     0.10,
        "success":  0.30,
    },
    "code_example": {
        "quality":  0.60,
        "latency":  0.10,
        "cost":     0.10,
        "success":  0.20,
    },
    "explanation": {
        "quality":  0.40,
        "latency":  0.40,
        "cost":     0.20,
        "success":  0.00,
    },
    "socratic": {
        "quality":  0.35,
        "latency":  0.40,
        "cost":     0.25,
        "success":  0.00,
    },
    # catch-all
    "default": {
        "quality":  0.45,
        "latency":  0.30,
        "cost":     0.15,
        "success":  0.10,
    },
}


class AdaptiveRouterEngine:
    """
    Central Adaptive Router Engine for AdaptRoute-Edu.

    Pipeline:
      extract_features → capability_filter → active_policy.select_model
    """

    def __init__(self):
        self.heuristic_policy = HeuristicRouterPolicy()
        self.bandit_policy = BanditRouterPolicy()
        self.capability_filter = CapabilityFilter(threshold=0.70)
        self.active_policy_name: str = getattr(settings, "ROUTER_POLICY", "heuristic")

    @property
    def active_policy(self) -> BaseRoutingPolicy:
        if self.active_policy_name == "bandit":
            return self.bandit_policy
        return self.heuristic_policy

    def load_bandit_state(self, db) -> bool:
        """Load LinUCB matrices A/b from the database for all registered models."""
        from app.repositories.linucb_repository import LinUCBRepository
        repo = LinUCBRepository(db)
        success = False
        for model_id in MODEL_REGISTRY.keys():
            res = repo.load_arm_state(model_id, self.bandit_policy.FEATURE_DIM)
            if res:
                A, b = res
                self.bandit_policy.set_arm_state(model_id, A, b)
                logger.debug(f"Loaded persisted LinUCB state for model arm: {model_id}")
                success = True
        return success

    def save_bandit_state(self, db, model_id: str) -> bool:
        """Persist LinUCB matrices A/b to the database for a specific model arm."""
        from app.repositories.linucb_repository import LinUCBRepository
        repo = LinUCBRepository(db)
        # Ensure arm is initialized if not present
        self.bandit_policy._init_arm(model_id)
        A = self.bandit_policy.A[model_id]
        b = self.bandit_policy.b[model_id]
        success = repo.save_arm_state(model_id, A, b)
        logger.debug(f"Saved LinUCB state for model arm: {model_id}")
        return success

    # ── Model Discovery ───────────────────────────────────────────────────────

    def get_available_models(self) -> List[str]:
        """
        Query the local Ollama daemon for installed model tags.
        Falls back to the configured primary model if Ollama is unreachable.
        """
        try:
            import json
            import urllib.request

            req = urllib.request.Request(
                f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/tags"
            )
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                installed = [
                    m["name"] for m in data.get("models", []) if "name" in m
                ]
                if installed:
                    return installed
        except Exception:
            pass
        return [settings.LLM_MODEL]

    # ── Main Routing Pipeline ─────────────────────────────────────────────────

    def route_task(
        self,
        task_type: str,
        prompt: str,
        user_skill_level: str = "beginner",
        preferred_pace: str = "moderate",
        daily_study_time: int = 60,
        forced_model: Optional[str] = None,
    ) -> Dict:
        """
        Route a tutoring task through the three-stage pipeline.

        Returns a dict with:
          selected_model, profile, features, candidates, routing_policy_used
        """
        available = self.get_available_models()

        # ── Manual override ───────────────────────────────────────────────────
        if forced_model and forced_model in available:
            features = extract_features(
                task_type, prompt, user_skill_level, preferred_pace, daily_study_time
            )
            return {
                "selected_model": forced_model,
                "profile": get_model_profile(forced_model),
                "features": features,
                "candidates": [(forced_model, 1.0)],
                "routing_policy_used": "manual_override",
            }

        # Stage 1: Feature extraction
        features = extract_features(
            task_type, prompt, user_skill_level, preferred_pace, daily_study_time
        )

        # Stage 2: Capability filter → ranked candidate list
        candidates = self.capability_filter.filter_capable_models(features, available)

        logger.debug(
            f"Router candidates for '{task_type}': "
            + ", ".join(f"{m}({s:.2f})" for m, s in candidates)
        )

        # Stage 3: Policy selects from capable candidates only
        selected_model = self.active_policy.select_model(features, candidates)
        profile = get_model_profile(selected_model)

        return {
            "selected_model": selected_model,
            "profile": profile,
            "features": features,
            "candidates": candidates,
            "routing_policy_used": self.active_policy_name,
        }

    # ── Quality-Based Escalation ──────────────────────────────────────────────

    def escalate_if_needed(
        self,
        original_model: str,
        quality_score: float,
        quality_threshold: float,
        task_type: str,
        prompt: str,
        user_skill_level: str = "beginner",
        preferred_pace: str = "moderate",
        daily_study_time: int = 60,
    ) -> Optional[str]:
        """
        If quality_score is below quality_threshold, find the next capable
        model (excluding original_model and lower-tier models).

        Returns the escalated model ID, or None if no escalation is needed
        or no better model is available.
        """
        if quality_score >= quality_threshold:
            return None

        available = self.get_available_models()
        available_excl = [m for m in available if m != original_model]
        if not available_excl:
            return None

        features = extract_features(
            task_type, prompt, user_skill_level, preferred_pace, daily_study_time
        )
        candidates = self.capability_filter.filter_capable_models(
            features, available_excl
        )

        # Prefer a higher-tier model
        original_profile = get_model_profile(original_model)
        tier_rank = {"lightweight": 0, "standard": 1, "heavy": 2}
        original_rank = tier_rank.get(original_profile.tier, 0)

        better_candidates = [
            (m, s)
            for m, s in candidates
            if tier_rank.get(get_model_profile(m).tier, 0) > original_rank
        ]

        target_candidates = better_candidates if better_candidates else candidates
        if not target_candidates:
            return None

        escalated = self.active_policy.select_model(features, target_candidates)
        logger.info(
            f"🔺 Escalating from '{original_model}' → '{escalated}' "
            f"(quality={quality_score:.2f} < threshold={quality_threshold:.2f})"
        )
        return escalated

    def score_and_escalate(
        self,
        response_text: str,
        original_model: str,
        task_type: str,
        prompt: str,
        quality_threshold: float = 0.65,
        user_skill_level: str = "beginner",
        preferred_pace: str = "moderate",
        daily_study_time: int = 60,
    ) -> Dict:
        """
        Convenience method that:
          1. Scores response_text with the heuristic quality evaluator
          2. Escalates to a better model if quality < threshold
          3. Returns a dict with quality_report and escalated_model (or None)

        This closes the adaptive loop so services don't need to import
        the evaluator directly.

        Example usage in a service:

            result = await provider.generate(prompt)
            escalation = router_engine.score_and_escalate(
                response_text=result.text,
                original_model=provider.model,
                task_type="roadmap",
                prompt=prompt,
            )
            if escalation["escalated_model"]:
                provider2 = get_provider(
                    task_type=task_type,
                    forced_model=escalation["escalated_model"]
                )
                result = await provider2.generate(prompt)
        """
        from .evaluator import evaluate_response
        requires_json = task_type in ("roadmap", "quiz")
        requires_code = task_type in ("code_example",)

        report = evaluate_response(
            response_text=response_text,
            task_type=task_type,
            prompt=prompt,
            requires_json=requires_json,
            requires_code=requires_code,
        )

        logger.info(
            f"Quality report for '{task_type}' via '{original_model}': "
            f"overall={report.overall:.2f} "
            f"[completeness={report.completeness:.2f}, "
            f"length={report.length_adequacy:.2f}, "
            f"structure={report.structure:.2f}]"
        )

        escalated_model = self.escalate_if_needed(
            original_model=original_model,
            quality_score=report.overall,
            quality_threshold=quality_threshold,
            task_type=task_type,
            prompt=prompt,
            user_skill_level=user_skill_level,
            preferred_pace=preferred_pace,
            daily_study_time=daily_study_time,
        )

        return {
            "quality_report": report,
            "escalated_model": escalated_model,
        }

    # ── Reward Computation ────────────────────────────────────────────────────

    def compute_reward(
        self,
        latency_ms: int,
        prompt_tokens: int,
        completion_tokens: int,
        model_id: str,
        task_type: str = "default",
        quiz_passed: Optional[bool] = None,
        quality_score: Optional[float] = None,
    ) -> float:
        """
        Multi-objective reward with task-dependent weights.

          Reward = w_quality × quality
                 + w_latency × latency_efficiency
                 – w_cost    × cost_penalty
                 + w_success × success

        quality_score: caller-supplied 0.0–1.0 quality estimate (optional).
        quiz_passed:   for quiz/roadmap tasks where a concrete outcome is known.
        """
        weights = _REWARD_WEIGHTS.get(task_type, _REWARD_WEIGHTS["default"])
        profile = get_model_profile(model_id)

        # 1. Quality component
        if quality_score is not None:
            quality = quality_score
        elif quiz_passed is True:
            quality = 0.90
        elif quiz_passed is False:
            quality = 0.40
        else:
            quality = 0.65  # neutral when no signal available

        # 2. Latency efficiency (normalised against a 3 000 ms baseline)
        latency_eff = max(0.0, 1.0 - latency_ms / 3000.0)

        # 3. Cost penalty (local Ollama = 0 cost, cloud models have real cost)
        est_cost = (
            (prompt_tokens / 1000.0) * profile.cost_per_1k_input
            + (completion_tokens / 1000.0) * profile.cost_per_1k_output
        )
        cost_penalty = min(1.0, est_cost * 100.0)

        # 4. Success signal (quiz pass / task completion)
        if quiz_passed is True:
            success = 1.0
        elif quiz_passed is False:
            success = 0.0
        else:
            success = 0.5

        total = (
            weights["quality"]  * quality
            + weights["latency"]  * latency_eff
            - weights["cost"]     * cost_penalty
            + weights["success"]  * success
        )
        return round(total, 4)


# ── Global singleton ──────────────────────────────────────────────────────────
router_engine = AdaptiveRouterEngine()

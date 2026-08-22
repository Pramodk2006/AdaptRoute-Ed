"""
Adaptive LLM Service — orchestrates the end-to-end adaptive routing loop:
1. Feature Extraction
2. Capability Filtering
3. Model Selection (Heuristic / LinUCB)
4. LLM Generation
5. Quality Evaluation
6. Optional Quality-Based Escalation
7. Multi-Objective Reward Computation
8. Online Bandit Parameter Updates & PostgreSQL Persistence
9. Unified Telemetry Logging
"""
import uuid
import time
import asyncio
from typing import Any, Dict, List, Optional, Tuple

from app.llm.base import LLMProvider, LLMResponse
from app.llm.factory import get_provider
from app.router import router_engine, extract_features, evaluate_response
from app.router.registry import get_model_profile
from app.repositories.routing_repository import RoutingRepository
from app.utils.logger import logger


class AdaptiveLLMService:
    @staticmethod
    async def generate(
        db_session,
        user_id: uuid.UUID,
        task_type: str,
        prompt: str,
        user_skill_level: str = "beginner",
        preferred_pace: str = "moderate",
        daily_study_time: int = 60,
        forced_model: Optional[str] = None,
        quality_threshold: float = 0.65,
        max_escalation_attempts: int = 2,
        is_json: bool = False,
        **generation_kwargs,
    ) -> LLMResponse:
        """
        Generate educational content through the adaptive router pipeline.

        Performs: Select model -> Generate -> Evaluate -> Escalate (if needed) -> Reward -> Update -> Telemetry
        """
        start_time = time.perf_counter()
        routing_repo = RoutingRepository(db_session) if db_session else None

        # ── Step 1: Load persisted LinUCB matrices ────────────────────────────
        if db_session and router_engine.active_policy_name == "bandit":
            try:
                router_engine.load_bandit_state(db_session)
            except Exception as e:
                logger.error(f"Failed to load bandit state: {e}. Falling back to in-memory.")

        # ── Step 2: Route task ────────────────────────────────────────────────
        route_decision = router_engine.route_task(
            task_type=task_type,
            prompt=prompt,
            user_skill_level=user_skill_level,
            preferred_pace=preferred_pace,
            daily_study_time=daily_study_time,
            forced_model=forced_model,
        )
        selected_model = route_decision["selected_model"]
        features = route_decision["features"]
        candidates = route_decision["candidates"]

        # Loop variables
        current_model = selected_model
        attempts = 0
        escalation_triggered = False
        escalation_model = None
        
        # ── Step 3: Generation & Escalation Loop ──────────────────────────────
        while True:
            # Check model availability/errors
            try:
                provider = get_provider(
                    task_type=task_type,
                    prompt=prompt,
                    user_skill_level=user_skill_level,
                    preferred_pace=preferred_pace,
                    daily_study_time=daily_study_time,
                    forced_model=current_model,
                )

                actual_prompt = prompt
                if is_json:
                    actual_prompt = (
                        prompt
                        + "\n\nIMPORTANT: Respond ONLY with valid JSON. "
                        "Do not include any markdown, explanation, or prose outside the JSON."
                    )
                response = await provider.generate(actual_prompt, **generation_kwargs)
                
                # Check for provider failure/fallback text
                if "AdaptRoute AI Tutor (Fallback)" in response.text or "Topic Quiz" in response.text and response.latency_ms <= 51:
                     # Treat fallback response as failure to trigger escalation
                     quality_passed = False
                     quality_score = 0.10
                     report = None
                else:
                     # ── Step 4: Quality Evaluation ───────────────────────────────
                     report = evaluate_response(
                         response_text=response.text,
                         task_type=task_type,
                         prompt=prompt,
                         requires_json=is_json,
                         requires_code=(task_type == "code_example"),
                     )
                     quality_score = report.overall
                     quality_passed = quality_score >= quality_threshold
            except Exception as e:
                logger.error(f"Generation error on model '{current_model}': {e}")
                quality_passed = False
                quality_score = 0.0
                report = None

            # Determine if escalation is needed
            if quality_passed or attempts >= max_escalation_attempts:
                break

            # Find next capable candidate
            next_model = router_engine.escalate_if_needed(
                original_model=current_model,
                quality_score=quality_score,
                quality_threshold=quality_threshold,
                task_type=task_type,
                prompt=prompt,
                user_skill_level=user_skill_level,
                preferred_pace=preferred_pace,
                daily_study_time=daily_study_time,
            )

            if not next_model or next_model == current_model:
                logger.info(f"No higher tier candidate available to escalate from '{current_model}'")
                break

            logger.info(
                f"Escalating: '{current_model}' (quality={quality_score:.2f}) "
                f"-> '{next_model}' (attempt {attempts + 1}/{max_escalation_attempts})"
            )
            escalation_triggered = True
            escalation_model = next_model
            current_model = next_model
            attempts += 1

        total_latency_ms = (time.perf_counter() - start_time) * 1000

        # ── Step 5: Reward calculation ────────────────────────────────────────
        # Reward is based on the initial model's performance to guide bandit learning
        reward = router_engine.compute_reward(
            latency_ms=int(response.latency_ms),
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            model_id=selected_model,
            task_type=task_type,
            quality_score=quality_score,
        )

        # ── Step 6: Online bandit parameter update ────────────────────────────
        bandit_updated = False
        if router_engine.active_policy_name == "bandit":
            try:
                router_engine.bandit_policy.update_reward(
                    model_id=selected_model,
                    features=features,
                    reward=reward,
                )
                bandit_updated = True
                
                # Save updated state to PostgreSQL
                if db_session:
                    router_engine.save_bandit_state(db_session, selected_model)
            except Exception as e:
                logger.error(f"Bandit parameter update failed: {e}")

        # ── Step 7: Telemetry / Database Logging ──────────────────────────────
        if routing_repo:
            try:
                routing_repo.log_decision(
                    user_id=user_id,
                    task_type=task_type,
                    selected_model=selected_model,
                    routing_policy_used=router_engine.active_policy_name,
                    prompt_length_chars=len(prompt),
                    user_skill_level=user_skill_level,
                    latency_ms=int(total_latency_ms),
                    prompt_tokens=response.prompt_tokens,
                    completion_tokens=response.completion_tokens,
                    estimated_cost_usd=0.0,  # Statically 0.0 for local models
                    reward_score=reward,
                    status="success",
                    quality_score=quality_score,
                    quality_passed=quality_passed,
                    escalation_triggered=escalation_triggered,
                    escalation_model=escalation_model,
                    escalation_attempts=attempts,
                    final_model=current_model,
                    bandit_update_performed=bandit_updated,
                )
            except Exception as e:
                logger.error(f"Failed to save telemetry log: {e}")

        # Return response object carrying total latency
        response.latency_ms = total_latency_ms
        return response

    @staticmethod
    async def generate_stream(
        db_session,
        user_id: uuid.UUID,
        task_type: str,
        prompt: str,
        user_skill_level: str = "beginner",
        preferred_pace: str = "moderate",
        daily_study_time: int = 60,
        forced_model: Optional[str] = None,
        **generation_kwargs,
    ):
        """
        Yield token stream, then calculate reward and update bandit metrics asynchronously.
        """
        start_time = time.perf_counter()
        routing_repo = RoutingRepository(db_session) if db_session else None

        # Load bandit state
        if db_session and router_engine.active_policy_name == "bandit":
            try:
                router_engine.load_bandit_state(db_session)
            except Exception as e:
                logger.error(f"Failed to load bandit state for stream: {e}")

        # Route task
        route_decision = router_engine.route_task(
            task_type=task_type,
            prompt=prompt,
            user_skill_level=user_skill_level,
            preferred_pace=preferred_pace,
            daily_study_time=daily_study_time,
            forced_model=forced_model,
        )
        selected_model = route_decision["selected_model"]
        features = route_decision["features"]

        provider = get_provider(
            task_type=task_type,
            prompt=prompt,
            user_skill_level=user_skill_level,
            preferred_pace=preferred_pace,
            daily_study_time=daily_study_time,
            forced_model=selected_model,
        )

        full_response_text = []
        token_count = 0

        # Stream generation
        if hasattr(provider, "generate_stream"):
            async for token in provider.generate_stream(prompt, **generation_kwargs):
                full_response_text.append(token)
                token_count += 1
                yield token
        else:
            res = await provider.generate(prompt, **generation_kwargs)
            token = res.text
            full_response_text.append(token)
            yield token

        total_latency_ms = (time.perf_counter() - start_time) * 1000
        response_text = "".join(full_response_text)

        # Defer evaluation and reward logging to background
        try:
            report = evaluate_response(
                response_text=response_text,
                task_type=task_type,
                prompt=prompt,
                requires_json=False,
                requires_code=(task_type == "code_example"),
            )
            reward = router_engine.compute_reward(
                latency_ms=int(total_latency_ms),
                prompt_tokens=len(prompt.split()),
                completion_tokens=token_count if token_count > 0 else len(response_text.split()),
                model_id=selected_model,
                task_type=task_type,
                quality_score=report.overall,
            )

            # Update bandit
            bandit_updated = False
            if router_engine.active_policy_name == "bandit":
                router_engine.bandit_policy.update_reward(
                    model_id=selected_model,
                    features=features,
                    reward=reward,
                )
                bandit_updated = True
                if db_session:
                    router_engine.save_bandit_state(db_session, selected_model)

            # Log telemetry
            if routing_repo:
                routing_repo.log_decision(
                    user_id=user_id,
                    task_type=task_type,
                    selected_model=selected_model,
                    routing_policy_used=router_engine.active_policy_name,
                    prompt_length_chars=len(prompt),
                    user_skill_level=user_skill_level,
                    latency_ms=int(total_latency_ms),
                    prompt_tokens=len(prompt.split()),
                    completion_tokens=token_count,
                    reward_score=reward,
                    status="success",
                    quality_score=report.overall,
                    quality_passed=report.overall >= 0.65,
                    escalation_triggered=False,
                    escalation_attempts=0,
                    final_model=selected_model,
                    bandit_update_performed=bandit_updated,
                )
        except Exception as e:
            logger.error(f"Failed to execute deferred streaming telemetry update: {e}")

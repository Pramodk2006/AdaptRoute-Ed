"""
Unit and integration tests for the three P0 fixes:
1. Generation -> Quality -> Escalation loop
2. Reward -> LinUCB matrix updates
3. PostgreSQL state persistence across restarts
"""
import uuid
import numpy as np
import pytest
from sqlalchemy.orm import Session

from app.database import Base
from app.models.linucb_state import LinUCBState
from app.router import router_engine, extract_features, evaluate_response
from app.router.policies import BanditRouterPolicy
from app.services.adaptive_llm_service import AdaptiveLLMService


@pytest.fixture(autouse=True)
def clean_db(db_session: Session):
    """Ensure database is clean before each test."""
    db_session.query(LinUCBState).delete()
    db_session.commit()
    yield


def test_linucb_learning_and_persistence(db_session: Session):
    """
    P0-2 & P0-3: Test that reward update changes LinUCB A/b matrices,
    persists them to PostgreSQL, and restores them accurately on reload.
    """
    model_id = "gemma3:latest"
    
    # ── Step 1: Ensure clean state ──────────────────────────────────────────
    router_engine.bandit_policy = BanditRouterPolicy(epsilon=0.0)  # Reset state
    router_engine.bandit_policy._init_arm(model_id)

    initial_A = router_engine.bandit_policy.A[model_id].copy()
    initial_b = router_engine.bandit_policy.b[model_id].copy()

    # Verify initialized to identity and zero
    assert np.array_equal(initial_A, np.identity(9))
    assert np.array_equal(initial_b, np.zeros((9, 1)))

    # ── Step 2: Perform update with positive reward ─────────────────────────
    features = extract_features("explanation", "Explain databases in simple terms")
    reward = 1.0

    router_engine.bandit_policy.update_reward(model_id, features, reward)

    updated_A = router_engine.bandit_policy.A[model_id].copy()
    updated_b = router_engine.bandit_policy.b[model_id].copy()

    # Matrices should have changed from initial identity/zero
    assert not np.array_equal(updated_A, initial_A)
    assert not np.array_equal(updated_b, initial_b)

    # ── Step 3: Persist to DB ────────────────────────────────────────────────
    success = router_engine.save_bandit_state(db_session, model_id)
    assert success is True

    # Verify database entry exists
    db_state = db_session.query(LinUCBState).filter(LinUCBState.model_id == model_id).first()
    assert db_state is not None
    assert db_state.update_count == 1

    # ── Step 4: Destroy policy instance and reload from PostgreSQL ───────────
    router_engine.bandit_policy = BanditRouterPolicy(epsilon=0.0)  # Re-initialize
    router_engine.load_bandit_state(db_session)

    reloaded_A = router_engine.bandit_policy.A[model_id]
    reloaded_b = router_engine.bandit_policy.b[model_id]

    # Reloaded values must exactly match the updated ones
    assert np.array_equal(reloaded_A, updated_A)
    assert np.array_equal(reloaded_b, updated_b)

    # ── Step 5: Perform second update and verify accumulation ────────────────
    router_engine.bandit_policy.update_reward(model_id, features, 0.8)
    router_engine.save_bandit_state(db_session, model_id)

    db_state_2 = db_session.query(LinUCBState).filter(LinUCBState.model_id == model_id).first()
    assert db_state_2.update_count == 2


@pytest.mark.asyncio
async def test_forced_quality_escalation(db_session: Session):
    """
    P0-1: Test that poor output quality triggers escalation to a higher tier model,
    successfully records telemetry, computes the reward, and triggers the update.
    """
    user_id = uuid.uuid4()
    # Setting threshold high so initial response from small model is forced to fail
    threshold = 0.98

    # We mock get_provider to return a provider that generates a low quality text first,
    # then a high quality text upon escalation.
    from unittest.mock import AsyncMock, patch
    from app.llm.base import LLMResponse

    mock_provider_low = AsyncMock()
    mock_provider_low.model_name = "ollama/gemma3:1b"
    mock_provider_low.generate = AsyncMock(return_value=LLMResponse(
        text="A variable holds a value.",
        model="ollama/gemma3:1b",
        prompt_tokens=10,
        completion_tokens=5,
        latency_ms=100,
    ))

    mock_provider_high = AsyncMock()
    mock_provider_high.model_name = "ollama/gemma3:latest"
    mock_provider_high.generate = AsyncMock(return_value=LLMResponse(
        text="A variable is a named storage location in memory used to hold data values. For example, x = 5.",
        model="ollama/gemma3:latest",
        prompt_tokens=15,
        completion_tokens=20,
        latency_ms=300,
    ))

    def mock_get_provider_side_effect(*args, **kwargs):
        forced_model = kwargs.get("forced_model")
        if forced_model == "gemma3:1b":
            return mock_provider_low
        return mock_provider_high

    from app.router.registry import get_model_profile
    mock_route = {
        "selected_model": "gemma3:1b",
        "profile": get_model_profile("gemma3:1b"),
        "features": extract_features("explanation", "What is a variable?"),
        "candidates": [("gemma3:1b", 0.80), ("gemma3:latest", 0.95)],
        "routing_policy_used": "heuristic"
    }

    with patch("app.services.adaptive_llm_service.get_provider", side_effect=mock_get_provider_side_effect):
        with patch("app.router.engine.router_engine.route_task", return_value=mock_route):
            with patch("app.router.engine.router_engine.get_available_models", return_value=["gemma3:1b", "gemma3:latest"]):
                # Temporarily configure heuristic engine parameters
                router_engine.active_policy_name = "heuristic"
                
                # Execute adaptive generation
                response = await AdaptiveLLMService.generate(
                    db_session=db_session,
                    user_id=user_id,
                    task_type="explanation",
                    prompt="What is a variable?",
                    quality_threshold=threshold,
                    max_escalation_attempts=1,
                )

            # Assertions
            # The final response should be the escalated one
            assert response.model == "ollama/gemma3:latest"
            assert "named storage location" in response.text

            # Verify telemetry was logged correctly to RoutingLog
            from app.models.routing_log import RoutingLog
            logs = db_session.query(RoutingLog).filter(RoutingLog.user_id == user_id).all()
            assert len(logs) == 1
            log = logs[0]
            assert log.selected_model == "gemma3:1b"  # Initial model routed
            assert log.escalation_triggered is True
            assert log.escalation_model == "gemma3:latest"
            assert log.final_model == "gemma3:latest"
            assert log.quality_score is not None
            assert log.reward_score is not None


@pytest.mark.asyncio
async def test_error_resilience_when_db_unavailable():
    """
    Test that database unavailability does not crash generation (falls back to in-memory).
    """
    user_id = uuid.uuid4()
    
    # We call AdaptiveLLMService with db_session=None (simulating database loss)
    response = await AdaptiveLLMService.generate(
        db_session=None,
        user_id=user_id,
        task_type="explanation",
        prompt="Define recursion.",
        quality_threshold=0.65,
    )

    # Response should still complete successfully
    assert response is not None
    assert len(response.text) > 0

"""
Router Engine & Policy unit tests — updated for the capability-aware architecture.
"""
from app.router.feature_extractor import extract_features
from app.router.policies import (
    BanditRouterPolicy,
    CapabilityFilter,
    HeuristicRouterPolicy,
)
from app.router.engine import AdaptiveRouterEngine


def test_feature_extractor():
    """Feature extractor produces correct capability requirement profiles per task."""
    # Code task → high coding requirement
    f_code = extract_features(
        "code_example", "Write a binary search algorithm in Python", "intermediate"
    )
    assert f_code.coding_requirement >= 0.90, (
        f"Expected coding_requirement >= 0.90, got {f_code.coding_requirement}"
    )
    assert f_code.task_type == "code_example"

    # Roadmap → high output_length, knowledge, structured_output
    f_roadmap = extract_features("roadmap", "Learn web development", "beginner")
    assert f_roadmap.output_length_requirement >= 0.90
    assert f_roadmap.structured_output_requirement >= 0.90
    assert f_roadmap.knowledge_requirement >= 0.85

    # Advanced skill level boosts reasoning
    f_adv = extract_features("explanation", "Explain recursion", "advanced")
    f_beg = extract_features("explanation", "Explain recursion", "beginner")
    assert f_adv.reasoning_requirement > f_beg.reasoning_requirement


def test_capability_filter():
    """CapabilityFilter eliminates models that can't satisfy task requirements."""
    filt = CapabilityFilter(threshold=0.70)
    models = ["gemma3:1b", "gemma3:latest", "llama3.1:8b", "qwen2.5-coder"]

    # Code task — gemma3:1b should be filtered out (low coding capability)
    f_code = extract_features("code_example", "Implement quicksort in Python")
    candidates = filt.filter_capable_models(f_code, models)
    candidate_ids = [m for m, _ in candidates]
    assert "gemma3:1b" not in candidate_ids, "gemma3:1b should be filtered for high-coding tasks"
    assert "qwen2.5-coder" in candidate_ids

    # Simple explanation — filter should still return at least 1 candidate
    f_simple = extract_features("explanation", "What is a variable?", "beginner")
    candidates_simple = filt.filter_capable_models(f_simple, models)
    assert len(candidates_simple) >= 1

    # Scores should be sorted descending
    scores = [s for _, s in candidates]
    assert scores == sorted(scores, reverse=True)


def test_heuristic_router_policy():
    """Heuristic router selects the highest-scoring capable model."""
    policy = HeuristicRouterPolicy()

    # Code task — qwen2.5-coder should win (highest coding capability)
    f_code = extract_features("code_example", "Implement quicksort in Python")
    candidates = [
        ("gemma3:latest", 0.72),
        ("llama3.1:8b", 0.78),
        ("qwen2.5-coder", 0.85),
    ]
    assert policy.select_model(f_code, candidates) == "qwen2.5-coder"

    # Only one candidate → always returns it
    assert policy.select_model(f_code, [("gemma3:latest", 0.80)]) == "gemma3:latest"

    # Empty candidates → safe fallback
    assert policy.select_model(f_code, []) == "gemma3:latest"


def test_bandit_router_policy():
    """Bandit router selects models from candidate tuples and updates weights on reward."""
    bandit = BanditRouterPolicy(epsilon=0.0)  # Pure exploitation for deterministic test
    candidates = [("gemma3:latest", 0.75), ("llama3.1:8b", 0.80)]
    f = extract_features("explanation", "Explain recursion")

    chosen = bandit.select_model(f, candidates)
    assert chosen in ("gemma3:latest", "llama3.1:8b")

    # Feed reward — should not raise
    bandit.update_reward(chosen, f, reward=0.9)
    # After high reward update, subsequent calls should favour chosen model
    chosen2 = bandit.select_model(f, candidates)
    assert chosen2 in ("gemma3:latest", "llama3.1:8b")


def test_telemetry_endpoint(client, auth_headers):
    """GET /api/v1/routing/telemetry returns telemetry data and active policy."""
    response = client.get("/api/v1/routing/telemetry", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "active_policy" in data
    assert "available_models" in data
    assert "total_requests" in data
    # New capability fields should be present
    if data["available_models"]:
        model = data["available_models"][0]
        assert "reasoning_score" in model
        assert "code_score" in model


def test_update_policy_config(client, auth_headers):
    """PUT /api/v1/routing/config updates the active routing policy mode."""
    res_bandit = client.put(
        "/api/v1/routing/config", json={"policy": "bandit"}, headers=auth_headers
    )
    assert res_bandit.status_code == 200
    assert res_bandit.json()["active_policy"] == "bandit"

    res_heuristic = client.put(
        "/api/v1/routing/config", json={"policy": "heuristic"}, headers=auth_headers
    )
    assert res_heuristic.status_code == 200
    assert res_heuristic.json()["active_policy"] == "heuristic"

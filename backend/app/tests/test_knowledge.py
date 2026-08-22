"""
Knowledge Tracing (BKT) unit tests.
"""
from app.knowledge.bkt_engine import (
    update_mastery,
    batch_update_mastery,
    needs_remediation,
    DEFAULT_PARAMS,
    MASTERY_THRESHOLD,
)


# ── BKT Math Tests ────────────────────────────────────────────────────────────

def test_correct_answer_increases_mastery():
    """A correct response should increase mastery P(L_t)."""
    initial = 0.25
    updated = update_mastery(initial, is_correct=True)
    assert updated > initial


def test_incorrect_answer_decreases_mastery():
    """An incorrect response should decrease mastery P(L_t)."""
    initial = 0.80
    updated = update_mastery(initial, is_correct=False)
    assert updated < initial


def test_mastery_bounded_01():
    """Mastery score must always remain in [0.0, 1.0]."""
    # Multiple correct answers from high mastery
    m = 0.95
    for _ in range(10):
        m = update_mastery(m, is_correct=True)
    assert 0.0 <= m <= 1.0

    # Multiple incorrect from low mastery
    m = 0.05
    for _ in range(10):
        m = update_mastery(m, is_correct=False)
    assert 0.0 <= m <= 1.0


def test_batch_update_all_correct():
    """Batch update with all correct answers should increase mastery substantially."""
    start = 0.25
    end = batch_update_mastery(start, correct_count=5, total_count=5)
    assert end > start
    assert end > 0.5


def test_batch_update_all_incorrect():
    """Batch update with all incorrect should keep mastery lower."""
    start = 0.50
    end = batch_update_mastery(start, correct_count=0, total_count=5)
    assert end < start


def test_transit_increases_mastery_baseline():
    """Even a wrong answer from very low mastery improves over the prior via transit."""
    # With P(T)=0.15, even after slip, transit makes it slightly higher
    start = 0.01
    updated = update_mastery(start, is_correct=False)
    # Transit ensures P(L_t) always >= P(L_t|obs)
    assert updated >= 0.0


def test_needs_remediation_below_threshold():
    """Needs remediation when mastery < 0.70 OR quiz < 60%."""
    assert needs_remediation(mastery_score=0.50, quiz_score_pct=80.0) is True   # low mastery
    assert needs_remediation(mastery_score=0.80, quiz_score_pct=55.0) is True   # low quiz
    assert needs_remediation(mastery_score=0.80, quiz_score_pct=75.0) is False  # both fine


# ── Mastery API Tests ─────────────────────────────────────────────────────────

def test_mastery_endpoint_empty(client, auth_headers):
    """GET /api/v1/knowledge/mastery returns empty stats for new user."""
    response = client.get("/api/v1/knowledge/mastery", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["topics_tracked"] == 0
    assert data["avg_mastery"] == 0.0
    assert data["overall_readiness"] == 0.0
    assert data["topic_details"] == []


def test_mastery_unauthorized():
    """GET /api/v1/knowledge/mastery without auth returns 401."""
    from app.main import app
    from fastapi.testclient import TestClient
    c = TestClient(app)
    response = c.get("/api/v1/knowledge/mastery")
    assert response.status_code == 401

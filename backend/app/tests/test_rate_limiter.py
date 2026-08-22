"""
Rate limiter unit tests.
"""
from fastapi import HTTPException
from app.utils.rate_limiter import SlidingWindowRateLimiter, check_llm_rate_limit


def test_sliding_window_rate_limiter_allows_under_limit():
    """Rate limiter allows requests under max limit."""
    limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=60)
    assert limiter.is_allowed("user_1") is True
    assert limiter.is_allowed("user_1") is True
    assert limiter.is_allowed("user_1") is True


def test_sliding_window_rate_limiter_blocks_over_limit():
    """Rate limiter blocks request once limit is reached."""
    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=60)
    assert limiter.is_allowed("user_2") is True
    assert limiter.is_allowed("user_2") is True
    assert limiter.is_allowed("user_2") is False


def test_check_llm_rate_limit_helper():
    """check_llm_rate_limit raises 429 when quota exhausted."""
    # Fake request mock object
    class FakeRequest:
        url = type("URL", (), {"path": "/api/v1/roadmap/generate"})()

    req = FakeRequest()
    test_user_id = "test_quota_user_123"

    # Fill up quota
    for _ in range(10):
        check_llm_rate_limit(req, test_user_id)

    # 11th request should raise HTTP 429
    try:
        check_llm_rate_limit(req, test_user_id)
        assert False, "Should have raised HTTPException 429"
    except HTTPException as e:
        assert e.status_code == 429
        assert "Rate limit exceeded" in e.detail

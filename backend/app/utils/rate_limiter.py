"""
Rate Limiter — Sliding window rate limiter middleware protecting LLM endpoints.
"""
import time
from collections import defaultdict, deque
from typing import Dict, Deque
from fastapi import HTTPException, Request, status
from app.utils.logger import logger


class SlidingWindowRateLimiter:
    """In-memory sliding window rate limiter per user/IP."""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # key -> deque of timestamps
        self._history: Dict[str, Deque[float]] = defaultdict(deque)

    def is_allowed(self, key: str) -> bool:
        """Check if request key exceeds maximum requests within window."""
        now = time.time()
        window_start = now - self.window_seconds
        user_timestamps = self._history[key]

        # Evict timestamps outside the window
        while user_timestamps and user_timestamps[0] < window_start:
            user_timestamps.popleft()

        if len(user_timestamps) >= self.max_requests:
            return False

        user_timestamps.append(now)
        return True


# Global rate limiter instances:
# 1. LLM Generation endpoints (max 10 generations / min per user)
llm_rate_limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=60)

# 2. General API endpoints (max 120 requests / min per IP)
general_rate_limiter = SlidingWindowRateLimiter(max_requests=120, window_seconds=60)


def check_llm_rate_limit(request: Request, user_id: str) -> None:
    """Dependency helper enforcing LLM generation rate limit."""
    key = f"llm_{user_id}"
    if not llm_rate_limiter.is_allowed(key):
        logger.warning(f"Rate limit exceeded for user '{user_id}' on endpoint {request.url.path}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded for LLM generation. Please wait 60 seconds before trying again.",
            headers={"Retry-After": "60"},
        )

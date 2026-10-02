"""
RateLimiter: token-bucket rate limiting per key.

Usage:
    rl = RateLimiter(rate=10, per_seconds=60)   # 10 per minute
    rl.check("user:123")                        # raises if exceeded
    rl.acquire("user:123")                      # consume one token

Thread-safe. Uses monotonic clock (immune to wall-clock changes).
"""

import time
from dataclasses import dataclass
from threading import Lock

from agents.limits.exceptions import RateLimitError


@dataclass
class _Bucket:
    """Token bucket state."""

    tokens: float
    last_refill: float


class RateLimiter:
    """
    Token-bucket rate limiter.

    Args:
        rate:          number of tokens added per interval
        per_seconds:   interval length in seconds (default 60)
        burst:         max tokens that can accumulate (default = rate)
    """

    def __init__(
        self,
        rate: int,
        per_seconds: float = 60.0,
        *,
        burst: int | None = None,
    ) -> None:
        if rate <= 0:
            raise ValueError("rate must be > 0")
        if per_seconds <= 0:
            raise ValueError("per_seconds must be > 0")

        self.rate = rate
        self.per_seconds = per_seconds
        self.burst = burst if burst is not None else rate
        self._buckets: dict[str, _Bucket] = {}
        self._lock = Lock()

    # ==========================================================
    # Public API
    # ==========================================================

    def check(self, key: str) -> None:
        """
        Raise RateLimitError if the key has no tokens left.

        Does NOT consume a token.
        """
        with self._lock:
            bucket = self._get_bucket(key)
            self._refill(bucket)
            if bucket.tokens < 1.0:
                retry_after = self._seconds_until_token(bucket)
                raise RateLimitError(
                    f"Rate limit exceeded for '{key}'. " f"Retry after {retry_after:.1f}s.",
                    retry_after=retry_after,
                )

    def acquire(self, key: str) -> None:
        """
        Consume one token; raise RateLimitError if none available.
        """
        with self._lock:
            bucket = self._get_bucket(key)
            self._refill(bucket)
            if bucket.tokens < 1.0:
                retry_after = self._seconds_until_token(bucket)
                raise RateLimitError(
                    f"Rate limit exceeded for '{key}'. " f"Retry after {retry_after:.1f}s.",
                    retry_after=retry_after,
                )
            bucket.tokens -= 1.0

    def remaining(self, key: str) -> int:
        """Return the number of tokens currently available."""
        with self._lock:
            bucket = self._get_bucket(key)
            self._refill(bucket)
            return int(bucket.tokens)

    def reset(self, key: str | None = None) -> None:
        """Reset one key or all keys (used in tests)."""
        with self._lock:
            if key is None:
                self._buckets.clear()
            else:
                self._buckets.pop(key, None)

    # ==========================================================
    # Internal
    # ==========================================================

    def _get_bucket(self, key: str) -> _Bucket:
        if key not in self._buckets:
            self._buckets[key] = _Bucket(tokens=float(self.burst), last_refill=time.monotonic())
        return self._buckets[key]

    def _refill(self, bucket: _Bucket) -> None:
        now = time.monotonic()
        elapsed = now - bucket.last_refill
        if elapsed <= 0:
            return
        tokens_per_second = self.rate / self.per_seconds
        bucket.tokens = min(float(self.burst), bucket.tokens + elapsed * tokens_per_second)
        bucket.last_refill = now

    def _seconds_until_token(self, bucket: _Bucket) -> float:
        if bucket.tokens >= 1.0:
            return 0.0
        tokens_per_second = self.rate / self.per_seconds
        missing = 1.0 - bucket.tokens
        return missing / tokens_per_second

"""Tests for RateLimiter."""

import time

import pytest

from agents.limits.exceptions import RateLimitError
from agents.limits.rate_limiter import RateLimiter


class TestRateLimiter:
    def test_allows_within_burst(self):
        rl = RateLimiter(rate=3, per_seconds=60)
        for _ in range(3):
            rl.acquire("user1")  # should not raise

    def test_blocks_over_burst(self):
        rl = RateLimiter(rate=2, per_seconds=60, burst=2)
        rl.acquire("user1")
        rl.acquire("user1")
        with pytest.raises(RateLimitError):
            rl.acquire("user1")

    def test_check_does_not_consume(self):
        rl = RateLimiter(rate=1, per_seconds=60, burst=1)
        rl.check("user1")
        rl.check("user1")
        rl.acquire("user1")  # ok
        with pytest.raises(RateLimitError):
            rl.acquire("user1")

    def test_keys_are_isolated(self):
        rl = RateLimiter(rate=1, per_seconds=60, burst=1)
        rl.acquire("user1")
        rl.acquire("user2")  # different key, should succeed

    def test_remaining_reflects_usage(self):
        rl = RateLimiter(rate=5, per_seconds=60, burst=5)
        assert rl.remaining("k") == 5
        rl.acquire("k")
        assert rl.remaining("k") == 4

    def test_reset_key(self):
        rl = RateLimiter(rate=1, per_seconds=60, burst=1)
        rl.acquire("k")
        rl.reset("k")
        rl.acquire("k")  # ok after reset

    def test_reset_all(self):
        rl = RateLimiter(rate=1, per_seconds=60, burst=1)
        rl.acquire("k1")
        rl.acquire("k2")
        rl.reset()
        rl.acquire("k1")
        rl.acquire("k2")

    def test_retry_after_is_positive_on_failure(self):
        rl = RateLimiter(rate=1, per_seconds=60, burst=1)
        rl.acquire("k")
        with pytest.raises(RateLimitError) as exc_info:
            rl.acquire("k")
        assert exc_info.value.retry_after > 0

    def test_refills_over_time(self):
        rl = RateLimiter(rate=10, per_seconds=1, burst=2)
        rl.acquire("k")
        rl.acquire("k")
        with pytest.raises(RateLimitError):
            rl.acquire("k")
        time.sleep(0.25)  # enough to refill ~2.5 tokens
        rl.acquire("k")  # should succeed

    def test_invalid_rate(self):
        with pytest.raises(ValueError):
            RateLimiter(rate=0)

    def test_invalid_per_seconds(self):
        with pytest.raises(ValueError):
            RateLimiter(rate=1, per_seconds=0)
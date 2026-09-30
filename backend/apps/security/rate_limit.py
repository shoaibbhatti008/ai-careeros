"""
Rate limiting helpers.

Uses Django's cache backend (Redis in production).
"""

from django.core.cache import cache


class RateLimitExceeded(Exception):
    """Raised when a rate limit is exceeded."""

    def __init__(self, retry_after: int = 60) -> None:
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after} seconds.")


def check_rate_limit(
    key: str,
    max_requests: int,
    window_seconds: int,
) -> tuple[bool, int]:
    """
    Increment a counter and check against a rate limit.

    Args:
        key: Unique key for the limit (e.g. f"login:{ip}").
        max_requests: Max requests allowed in the window.
        window_seconds: Time window in seconds.

    Returns:
        (allowed, remaining) tuple.

    Raises:
        Nothing — caller decides what to do.
    """
    cache_key = f"ratelimit:{key}"
    current = cache.get(cache_key, 0)

    if current >= max_requests:
        return False, 0

    # Increment with expiry
    if current == 0:
        cache.set(cache_key, 1, timeout=window_seconds)
    else:
        try:
            cache.incr(cache_key)
        except ValueError:
            # Key expired between get and incr
            cache.set(cache_key, 1, timeout=window_seconds)

    remaining = max_requests - (current + 1)
    return True, max(remaining, 0)


def get_client_ip(request) -> str:
    """Extract client IP from request, handling proxies."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")

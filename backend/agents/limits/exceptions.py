"""Exceptions for limits and cost control."""


class LimitError(Exception):
    """Base class for all limit-related errors."""

    def __init__(self, message: str, *, retry_after: float = 0.0) -> None:
        self.retry_after = retry_after
        super().__init__(message)


class RateLimitError(LimitError):
    """Raised when a rate limit is exceeded."""


class BudgetExceededError(LimitError):
    """Raised when a workflow/agent/tool budget is exceeded."""


class CostLimitExceededError(LimitError):
    """Raised when a cost limit is exceeded."""

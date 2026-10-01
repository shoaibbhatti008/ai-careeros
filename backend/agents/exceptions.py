"""
Custom exceptions for the agent framework.

These are deliberately explicit and typed so callers can handle them
selectively (e.g., retry on budget, block on permission).
"""


class AgentError(Exception):
    """Base class for all agent errors."""

    def __init__(self, message: str, *, agent_name: str | None = None) -> None:
        self.agent_name = agent_name
        super().__init__(message)


class AgentValidationError(AgentError):
    """Raised when input/output fails schema validation."""


class AgentPermissionError(AgentError):
    """Raised when an agent attempts an action it is not permitted to perform."""


class AgentBudgetExceededError(AgentError):
    """Raised when an agent exceeds its step/tool/time budget."""


class AgentToolNotFoundError(AgentError):
    """Raised when an agent references a tool that is not registered."""


class AgentToolNotAllowedError(AgentError):
    """Raised when an agent attempts to use a tool not in its allowlist."""


class AgentProviderError(AgentError):
    """Raised when the underlying LLM provider fails."""


class AgentTimeoutError(AgentError):
    """Raised when an agent execution exceeds its wall-clock timeout."""

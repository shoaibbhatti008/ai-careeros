"""Tool-specific errors."""


class ToolError(Exception):
    """Base class for all tool errors."""

    def __init__(self, message: str, *, tool_name: str | None = None) -> None:
        self.tool_name = tool_name
        super().__init__(message)


class ToolNotFoundError(ToolError):
    """Tool is not registered."""


class ToolNotAllowedError(ToolError):
    """Tool is not in the agent's allowlist."""


class ToolPermissionError(ToolError):
    """Tool is not permitted in the current context."""


class ToolInputError(ToolError):
    """Tool input failed validation."""


class ToolOutputError(ToolError):
    """Tool output failed validation."""


class ToolExecutionError(ToolError):
    """Tool execution failed."""


class ToolTimeoutError(ToolError):
    """Tool exceeded its timeout."""


class ToolRateLimitError(ToolError):
    """Tool rate limit exceeded."""

"""
BaseTool: abstract base class for all tools.

Every tool MUST declare:
    name            unique identifier
    description     human-readable
    risk_level      LOW | MEDIUM | HIGH | CRITICAL
    allowed_agents  frozenset of agent names that may call this tool
    input_schema    dict describing expected input
    output_schema   dict describing produced output
    timeout_seconds maximum execution time
    rate_limit      max calls per minute (0 = no limit)
    requires_approval  True if sensitive actions need user approval

Tools MUST NOT:
- Access the filesystem, env vars, or network directly
- Modify system state without explicit approval
- Execute arbitrary code
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ClassVar

from agents.tools.errors import (
    ToolError,
    ToolInputError,
    ToolOutputError,
)


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ToolContext:
    """
    Context passed to a tool during execution.

    Tools receive:
    - user_id:              opaque user identifier
    - trace_id:             for logging
    - metadata:             free-form per-request data
    - approval_granted:     True if a human approved this action
    """

    user_id: str
    trace_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    approval_granted: bool = False


@dataclass
class ToolResult:
    """Structured result from a tool."""

    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    duration_ms: int = 0

    @classmethod
    def ok(cls, data: dict[str, Any], duration_ms: int = 0) -> "ToolResult":
        return cls(success=True, data=data, duration_ms=duration_ms)

    @classmethod
    def fail(cls, error: str, duration_ms: int = 0) -> "ToolResult":
        return cls(success=False, error=error, duration_ms=duration_ms)


class BaseTool(ABC):
    """
    Abstract base for all tools.

    Subclasses declare class-level metadata and implement `run()`.
    """

    # ---- Required metadata ----
    name: ClassVar[str]
    description: ClassVar[str] = ""
    risk_level: ClassVar[RiskLevel] = RiskLevel.LOW
    allowed_agents: ClassVar[frozenset[str]] = frozenset()
    input_schema: ClassVar[dict[str, Any]] = {}
    output_schema: ClassVar[dict[str, Any]] = {}

    # ---- Limits ----
    timeout_seconds: ClassVar[int] = 30
    rate_limit_per_minute: ClassVar[int] = 60
    requires_approval: ClassVar[bool] = False

    def __init__(self, context: ToolContext) -> None:
        if not getattr(self, "name", None):
            raise ToolError(f"{self.__class__.__name__} must declare a class-level 'name'.")
        self.context = context

    def validate_input(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate input against the declared schema.

        Default implementation: check required fields.
        Subclasses may override for stricter validation.
        """
        schema = self.input_schema or {}
        required = schema.get("required", [])
        for field_name in required:
            if field_name not in input_data:
                raise ToolInputError(
                    f"Missing required input '{field_name}'.",
                    tool_name=self.name,
                )
        return input_data

    def validate_output(self, output_data: dict[str, Any]) -> dict[str, Any]:
        """
        Validate output against the declared schema.

        Default implementation: ensure it's a dict.
        Subclasses may override.
        """
        if not isinstance(output_data, dict):
            raise ToolOutputError(
                f"Tool '{self.name}' must return a dict.",
                tool_name=self.name,
            )
        return output_data

    def execute(self, input_data: dict[str, Any]) -> ToolResult:
        """
        Framework-controlled execution.

        - Validates input
        - Checks approval if required
        - Runs the tool
        - Validates output
        - Wraps errors
        """
        import time

        start = time.monotonic()

        # Approval check
        if self.requires_approval and not self.context.approval_granted:
            return ToolResult.fail(
                f"Tool '{self.name}' requires human approval.",
                duration_ms=0,
            )

        # Input validation
        try:
            input_data = self.validate_input(input_data)
        except ToolInputError as exc:
            return ToolResult.fail(f"Input validation failed: {exc}", duration_ms=0)

        # Run
        try:
            output_data = self.run(input_data)
        except ToolError as exc:
            elapsed = int((time.monotonic() - start) * 1000)
            return ToolResult.fail(str(exc), duration_ms=elapsed)
        except Exception as exc:
            elapsed = int((time.monotonic() - start) * 1000)
            return ToolResult.fail(
                f"Unhandled error in tool '{self.name}': {exc}",
                duration_ms=elapsed,
            )

        # Output validation
        try:
            output_data = self.validate_output(output_data)
        except ToolOutputError as exc:
            elapsed = int((time.monotonic() - start) * 1000)
            return ToolResult.fail(str(exc), duration_ms=elapsed)

        elapsed = int((time.monotonic() - start) * 1000)
        return ToolResult.ok(output_data, duration_ms=elapsed)

    @abstractmethod
    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Tool logic. Must return a dict.

        Must NOT:
        - Access filesystem / env / network directly
        - Execute arbitrary code
        - Modify global state

        Should:
        - Validate assumptions
        - Return structured data
        """
        raise NotImplementedError

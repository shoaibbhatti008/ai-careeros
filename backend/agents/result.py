"""
AgentResult: structured output from an agent.

Agents MUST return AgentResult — never raw dicts, never free-form text.
This makes it easy to:
- Validate outputs
- Store in the DB (as JSON)
- Pass to the verification agent
- Log / audit
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class AgentStatus(str, Enum):
    """Status of an agent execution."""

    COMPLETED = "completed"
    FAILED = "failed"
    AWAITING_APPROVAL = "awaiting_approval"
    CANCELLED = "cancelled"
    BUDGET_EXCEEDED = "budget_exceeded"


@dataclass
class AgentResult:
    """
    Structured result from an agent execution.

    Attributes:
        status:       Outcome of the execution.
        output:       Structured JSON output.
        summary:      Human-readable summary (short).
        error:        Error message if failed.
        citations:    Source attributions (for RAG agents).
        approvals:    List of proposed actions requiring user approval.
        usage:        Token/step usage.
        metadata:     Free-form extras.
    """

    status: AgentStatus
    output: dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    error: str = ""
    citations: list[dict[str, Any]] = field(default_factory=list)
    approvals: list[dict[str, Any]] = field(default_factory=list)
    usage: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def completed(
        cls,
        output: dict[str, Any],
        summary: str = "",
        *,
        citations: list[dict[str, Any]] | None = None,
        approvals: list[dict[str, Any]] | None = None,
        usage: dict[str, Any] | None = None,
    ) -> "AgentResult":
        """Helper: create a successful result."""
        return cls(
            status=AgentStatus.COMPLETED,
            output=output,
            summary=summary,
            citations=citations or [],
            approvals=approvals or [],
            usage=usage or {},
        )

    @classmethod
    def failed(
        cls,
        error: str,
        *,
        output: dict[str, Any] | None = None,
    ) -> "AgentResult":
        """Helper: create a failed result."""
        return cls(
            status=AgentStatus.FAILED,
            output=output or {},
            error=error,
        )

    @classmethod
    def awaiting_approval(
        cls,
        approvals: list[dict[str, Any]],
        summary: str = "",
    ) -> "AgentResult":
        """Helper: create a result that requires human approval."""
        return cls(
            status=AgentStatus.AWAITING_APPROVAL,
            summary=summary,
            approvals=approvals,
        )

    @property
    def is_success(self) -> bool:
        return self.status == AgentStatus.COMPLETED

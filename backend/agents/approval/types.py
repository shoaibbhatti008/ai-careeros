"""Data types for the approval workflow."""

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class ApprovalStatus(str, Enum):
    """Status of an approval request."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ApprovalAction(str, Enum):
    """Types of actions that require approval."""

    SEND_EMAIL = "send_email"
    SUBMIT_APPLICATION = "submit_application"
    EXPORT_DATA = "export_data"
    DELETE_DATA = "delete_data"
    EXTERNAL_API_CALL = "external_api_call"
    OTHER = "other"


@dataclass
class ApprovalRequest:
    """
    A request for user approval before executing a sensitive action.

    Attributes:
        request_id:     unique identifier
        user_id:        the user who must approve
        agent_name:     the agent that created this request
        action:         the type of action
        title:          short summary
        description:    longer explanation
        payload:        structured data the action will use
        status:         current status
        created_at:     when created
        expires_at:     auto-reject after this time (optional)
        decided_at:     when approved/rejected
        decision_note:  optional note from user
        decided_by:     who decided (usually user_id)
    """

    user_id: UUID
    agent_name: str
    action: ApprovalAction
    title: str
    request_id: UUID = field(default_factory=uuid4)
    description: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    decided_at: datetime | None = None
    decision_note: str = ""
    decided_by: UUID | None = None

    def is_expired(self, *, now: datetime | None = None) -> bool:
        """Return True if the request has passed its expiry."""
        if self.expires_at is None:
            return False
        now = now or datetime.now(UTC)
        return now >= self.expires_at

    def is_decidable(self) -> bool:
        """Return True if the request can still be approved/rejected."""
        return self.status == ApprovalStatus.PENDING and not self.is_expired()


@dataclass
class ApprovalDecision:
    """The result of a decision on an approval request."""

    request_id: UUID
    status: ApprovalStatus
    decided_at: datetime
    note: str = ""
    decided_by: UUID | None = None
    error: str = ""

    @property
    def is_approved(self) -> bool:
        return self.status == ApprovalStatus.APPROVED

    @property
    def is_rejected(self) -> bool:
        return self.status == ApprovalStatus.REJECTED

    @property
    def is_success(self) -> bool:
        return not self.error and self.status in (
            ApprovalStatus.APPROVED,
            ApprovalStatus.REJECTED,
        )


def default_expiry(hours: int = 24) -> datetime:
    """Default expiry timestamp."""
    return datetime.now(UTC) + timedelta(hours=hours)

"""Human-in-the-loop approval workflow.

Design principles:
- No sensitive action is executed without explicit user approval.
- Approval requests are structured, auditable, and have an expiry.
- The approval layer is provider-agnostic (in-memory for tests,
  Django-backed in production).
"""

from agents.approval.service import ApprovalService
from agents.approval.types import (
    ApprovalAction,
    ApprovalDecision,
    ApprovalRequest,
    ApprovalStatus,
)

__all__ = [
    "ApprovalAction",
    "ApprovalDecision",
    "ApprovalRequest",
    "ApprovalStatus",
    "ApprovalService",
]

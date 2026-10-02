"""
ApprovalService: in-memory approval workflow.

In production, replace with a Django-backed implementation that
persists to the `ApprovalRequest` model. The interface stays the same.

Safety:
- Requests are scoped by user_id.
- Approvals are one-shot (cannot re-decide).
- Expired requests are auto-rejected on decision.
"""

from datetime import UTC, datetime
from uuid import UUID

from agents.approval.types import (
    ApprovalAction,
    ApprovalDecision,
    ApprovalRequest,
    ApprovalStatus,
)


class ApprovalService:
    """
    In-memory approval service.

    Usage:
        svc = ApprovalService()
        req = svc.create_request(
            user_id=user_id,
            agent_name="email_agent",
            action=ApprovalAction.SEND_EMAIL,
            title="Send follow-up email",
            payload={"to": "...", "body": "..."},
        )
        decision = svc.approve(req.request_id, user_id=user_id, note="Looks good")
    """

    def __init__(self) -> None:
        self._requests: dict[UUID, ApprovalRequest] = {}

    # ==========================================================
    # Write
    # ==========================================================

    def create_request(
        self,
        *,
        user_id: UUID,
        agent_name: str,
        action: ApprovalAction,
        title: str,
        description: str = "",
        payload: dict | None = None,
        expires_at: datetime | None = None,
    ) -> ApprovalRequest:
        request = ApprovalRequest(
            user_id=user_id,
            agent_name=agent_name,
            action=action,
            title=title,
            description=description,
            payload=payload or {},
            expires_at=expires_at,
        )
        self._requests[request.request_id] = request
        return request

    def approve(
        self,
        request_id: UUID,
        *,
        user_id: UUID,
        note: str = "",
    ) -> ApprovalDecision:
        """Approve a pending request."""
        return self._decide(
            request_id,
            user_id=user_id,
            new_status=ApprovalStatus.APPROVED,
            note=note,
        )

    def reject(
        self,
        request_id: UUID,
        *,
        user_id: UUID,
        note: str = "",
    ) -> ApprovalDecision:
        """Reject a pending request."""
        return self._decide(
            request_id,
            user_id=user_id,
            new_status=ApprovalStatus.REJECTED,
            note=note,
        )

    def cancel(
        self,
        request_id: UUID,
        *,
        user_id: UUID,
        note: str = "",
    ) -> ApprovalDecision:
        """Cancel a pending request."""
        return self._decide(
            request_id,
            user_id=user_id,
            new_status=ApprovalStatus.CANCELLED,
            note=note,
        )

    # ==========================================================
    # Read
    # ==========================================================

    def get(self, request_id: UUID, *, user_id: UUID) -> ApprovalRequest | None:
        """Fetch a request by ID. Ownership enforced."""
        req = self._requests.get(request_id)
        if req is None or req.user_id != user_id:
            return None
        # Auto-expire on read
        if req.status == ApprovalStatus.PENDING and req.is_expired():
            req.status = ApprovalStatus.EXPIRED
        return req

    def list_pending(self, *, user_id: UUID) -> list[ApprovalRequest]:
        """List all pending requests for a user (auto-expiring stale ones)."""
        result: list[ApprovalRequest] = []
        for req in self._requests.values():
            if req.user_id != user_id:
                continue
            if req.status == ApprovalStatus.PENDING and req.is_expired():
                req.status = ApprovalStatus.EXPIRED
            if req.status == ApprovalStatus.PENDING:
                result.append(req)
        result.sort(key=lambda r: r.created_at)
        return result

    def list_all(self, *, user_id: UUID) -> list[ApprovalRequest]:
        """List all requests for a user (any status)."""
        result = [r for r in self._requests.values() if r.user_id == user_id]
        result.sort(key=lambda r: r.created_at, reverse=True)
        return result

    def clear(self) -> None:
        """Clear all requests (used in tests)."""
        self._requests.clear()

    # ==========================================================
    # Internal
    # ==========================================================

    def _decide(
        self,
        request_id: UUID,
        *,
        user_id: UUID,
        new_status: ApprovalStatus,
        note: str,
    ) -> ApprovalDecision:
        req = self._requests.get(request_id)
        if req is None:
            return ApprovalDecision(
                request_id=request_id,
                status=new_status,
                decided_at=datetime.now(UTC),
                error="Approval request not found.",
            )
        if req.user_id != user_id:
            return ApprovalDecision(
                request_id=request_id,
                status=new_status,
                decided_at=datetime.now(UTC),
                error="You do not own this approval request.",
            )
        if req.is_expired():
            req.status = ApprovalStatus.EXPIRED
            return ApprovalDecision(
                request_id=request_id,
                status=ApprovalStatus.EXPIRED,
                decided_at=datetime.now(UTC),
                error="Approval request has expired.",
            )
        if req.status != ApprovalStatus.PENDING:
            return ApprovalDecision(
                request_id=request_id,
                status=req.status,
                decided_at=datetime.now(UTC),
                error=f"Request is already {req.status.value}.",
            )

        req.status = new_status
        req.decided_at = datetime.now(UTC)
        req.decision_note = note
        req.decided_by = user_id

        return ApprovalDecision(
            request_id=request_id,
            status=new_status,
            decided_at=req.decided_at,
            note=note,
            decided_by=user_id,
        )

"""Tests for the approval workflow."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from agents.approval.service import ApprovalService
from agents.approval.types import (
    ApprovalAction,
    ApprovalStatus,
    default_expiry,
)
from agents.context import AgentBudgets, AgentContext
from agents.implementations.approval_agent import ApprovalAgent
from agents.registry import AgentRegistry
from agents.tools.base import ToolContext
from agents.tools.builtin.approval import RequestApprovalTool
from agents.tools.registry import ToolRegistry, execute_tool


# ==========================================================
# Service tests
# ==========================================================


class TestApprovalService:
    def test_create_request(self):
        svc = ApprovalService()
        user_id = uuid4()
        req = svc.create_request(
            user_id=user_id,
            agent_name="email_agent",
            action=ApprovalAction.SEND_EMAIL,
            title="Send email",
        )
        assert req.status == ApprovalStatus.PENDING
        assert req.user_id == user_id

    def test_approve_pending_request(self):
        svc = ApprovalService()
        user_id = uuid4()
        req = svc.create_request(
            user_id=user_id,
            agent_name="email_agent",
            action=ApprovalAction.SEND_EMAIL,
            title="Send email",
        )
        decision = svc.approve(req.request_id, user_id=user_id, note="OK")
        assert decision.is_approved is True
        assert decision.is_success is True

    def test_reject_request(self):
        svc = ApprovalService()
        user_id = uuid4()
        req = svc.create_request(
            user_id=user_id,
            agent_name="email_agent",
            action=ApprovalAction.SEND_EMAIL,
            title="Send email",
        )
        decision = svc.reject(req.request_id, user_id=user_id, note="No")
        assert decision.is_rejected is True

    def test_cannot_approve_twice(self):
        svc = ApprovalService()
        user_id = uuid4()
        req = svc.create_request(
            user_id=user_id,
            agent_name="agent",
            action=ApprovalAction.SEND_EMAIL,
            title="X",
        )
        svc.approve(req.request_id, user_id=user_id)
        decision = svc.approve(req.request_id, user_id=user_id)
        assert decision.is_success is False
        assert "already" in decision.error.lower()

    def test_cannot_approve_other_users_request(self):
        svc = ApprovalService()
        user_a = uuid4()
        user_b = uuid4()
        req = svc.create_request(
            user_id=user_a,
            agent_name="agent",
            action=ApprovalAction.SEND_EMAIL,
            title="X",
        )
        decision = svc.approve(req.request_id, user_id=user_b)
        assert decision.is_success is False
        assert "own" in decision.error.lower()

    def test_get_enforces_ownership(self):
        svc = ApprovalService()
        user_a = uuid4()
        user_b = uuid4()
        req = svc.create_request(
            user_id=user_a,
            agent_name="agent",
            action=ApprovalAction.SEND_EMAIL,
            title="X",
        )
        assert svc.get(req.request_id, user_id=user_b) is None

    def test_get_returns_own_request(self):
        svc = ApprovalService()
        user_id = uuid4()
        req = svc.create_request(
            user_id=user_id,
            agent_name="agent",
            action=ApprovalAction.SEND_EMAIL,
            title="X",
        )
        found = svc.get(req.request_id, user_id=user_id)
        assert found is not None
        assert found.request_id == req.request_id

    def test_list_pending(self):
        svc = ApprovalService()
        user_id = uuid4()
        svc.create_request(
            user_id=user_id,
            agent_name="a",
            action=ApprovalAction.SEND_EMAIL,
            title="1",
        )
        svc.create_request(
            user_id=user_id,
            agent_name="a",
            action=ApprovalAction.DELETE_DATA,
            title="2",
        )
        pending = svc.list_pending(user_id=user_id)
        assert len(pending) == 2

    def test_expired_request_auto_rejected(self):
        svc = ApprovalService()
        user_id = uuid4()
        past = datetime.now(timezone.utc) - timedelta(hours=1)
        req = svc.create_request(
            user_id=user_id,
            agent_name="a",
            action=ApprovalAction.SEND_EMAIL,
            title="X",
            expires_at=past,
        )
        decision = svc.approve(req.request_id, user_id=user_id)
        assert decision.is_success is False
        assert "expired" in decision.error.lower()

    def test_default_expiry(self):
        exp = default_expiry(hours=1)
        assert exp > datetime.now(timezone.utc)

    def test_unknown_request_returns_error(self):
        svc = ApprovalService()
        decision = svc.approve(uuid4(), user_id=uuid4())
        assert decision.is_success is False
        assert "not found" in decision.error.lower()


# ==========================================================
# Tool tests
# ==========================================================


class TestRequestApprovalTool:
    def test_creates_request(self):
        svc = ApprovalService()
        user_id = uuid4()
        tool = RequestApprovalTool(
            ToolContext(user_id=str(user_id), metadata={"approval_service": svc})
        )
        result = tool.execute(
            {
                "action": "send_email",
                "title": "Send follow-up",
                "payload": {"to": "user@example.com"},
            }
        )
        assert result.success is True
        assert "request_id" in result.data

    def test_invalid_action_fails(self):
        svc = ApprovalService()
        tool = RequestApprovalTool(
            ToolContext(user_id=str(uuid4()), metadata={"approval_service": svc})
        )
        result = tool.execute({"action": "invalid_action", "title": "X"})
        assert result.success is False

    def test_missing_service_fails(self):
        tool = RequestApprovalTool(ToolContext(user_id=str(uuid4())))
        result = tool.execute({"action": "send_email", "title": "X"})
        assert result.success is False
        assert "service" in result.error.lower()

    def test_missing_title_fails(self):
        svc = ApprovalService()
        tool = RequestApprovalTool(
            ToolContext(user_id=str(uuid4()), metadata={"approval_service": svc})
        )
        result = tool.execute({"action": "send_email"})
        assert result.success is False


# ==========================================================
# Agent tests
# ==========================================================


@pytest.fixture(autouse=True)
def register_approval_agent():
    ToolRegistry._tools.setdefault("request_approval", RequestApprovalTool)
    AgentRegistry._agents.setdefault("approval_agent", ApprovalAgent)
    yield


def _make_context(
    *,
    service: ApprovalService,
    user_id,
    allowed_tools: frozenset[str] | None = None,
) -> AgentContext:
    if allowed_tools is None:
        tools = frozenset({"request_approval"})
    else:
        tools = allowed_tools

    def tool_executor(tool_name: str, **kwargs: object) -> dict:
        tool_context = ToolContext(
            user_id=str(user_id),
            metadata={"approval_service": service},
        )
        return execute_tool(
            tool_name=tool_name,
            agent_name="approval_agent",
            agent_allowed_tools=ApprovalAgent.allowed_tools,
            context_allowed_tools=tools,
            input_data=dict(kwargs),
            tool_context=tool_context,
        )

    return AgentContext(
        user_id=user_id,
        allowed_tools=tools,
        tool_executor=tool_executor,
    )


class TestApprovalAgent:
    def test_creates_approval_request(self):
        svc = ApprovalService()
        user_id = uuid4()
        ctx = _make_context(service=svc, user_id=user_id)
        agent = ApprovalAgent(ctx)
        result = agent.execute(
            {
                "action": "send_email",
                "title": "Send follow-up email",
                "payload": {"to": "x@example.com"},
            }
        )
        assert result.status.value == "awaiting_approval"
        assert "request_id" in result.output
        assert len(result.approvals) == 1

    def test_missing_title_fails(self):
        svc = ApprovalService()
        ctx = _make_context(service=svc, user_id=uuid4())
        agent = ApprovalAgent(ctx)
        result = agent.execute({"action": "send_email"})
        assert result.status.value == "failed"

    def test_missing_action_fails(self):
        svc = ApprovalService()
        ctx = _make_context(service=svc, user_id=uuid4())
        agent = ApprovalAgent(ctx)
        result = agent.execute({"title": "X"})
        assert result.status.value == "failed"

    def test_request_is_persisted_in_service(self):
        svc = ApprovalService()
        user_id = uuid4()
        ctx = _make_context(service=svc, user_id=user_id)
        agent = ApprovalAgent(ctx)
        result = agent.execute({"action": "send_email", "title": "X"})
        request_id = result.output["request_id"]
        from uuid import UUID

        found = svc.get(UUID(request_id), user_id=user_id)
        assert found is not None
        assert found.title == "X"

    def test_agent_is_registered(self):
        assert AgentRegistry.get("approval_agent") is ApprovalAgent

    def test_agent_declares_one_tool(self):
        assert ApprovalAgent.allowed_tools == frozenset({"request_approval"})

    def test_respects_allowlist(self):
        svc = ApprovalService()
        ctx = _make_context(
            service=svc, user_id=uuid4(), allowed_tools=frozenset()
        )
        agent = ApprovalAgent(ctx)
        result = agent.execute({"action": "send_email", "title": "X"})
        assert result.status.value == "failed"

    def test_respects_budget(self):
        svc = ApprovalService()
        ctx = _make_context(service=svc, user_id=uuid4())
        ctx.budgets = AgentBudgets(max_tool_calls=0)
        agent = ApprovalAgent(ctx)
        result = agent.execute({"action": "send_email", "title": "X"})
        assert result.status.value == "failed"

    def test_summary_present(self):
        svc = ApprovalService()
        ctx = _make_context(service=svc, user_id=uuid4())
        agent = ApprovalAgent(ctx)
        result = agent.execute({"action": "send_email", "title": "Send email"})
        assert result.summary
        assert "Send email" in result.summary

    def test_multiple_requests_get_unique_ids(self):
        svc = ApprovalService()
        user_id = uuid4()
        ctx = _make_context(service=svc, user_id=user_id)
        agent = ApprovalAgent(ctx)
        r1 = agent.execute({"action": "send_email", "title": "A"})
        r2 = agent.execute({"action": "send_email", "title": "B"})
        assert r1.output["request_id"] != r2.output["request_id"]

    def test_payload_forwarded(self):
        svc = ApprovalService()
        user_id = uuid4()
        ctx = _make_context(service=svc, user_id=user_id)
        agent = ApprovalAgent(ctx)
        result = agent.execute(
            {
                "action": "send_email",
                "title": "X",
                "payload": {"to": "user@example.com", "subject": "Hi"},
            }
        )
        from uuid import UUID

        found = svc.get(UUID(result.output["request_id"]), user_id=user_id)
        assert found.payload["to"] == "user@example.com"


# ==========================================================
# End-to-end approval flow
# ==========================================================


class TestApprovalEndToEnd:
    def test_full_flow(self):
        """Request → approve → decision returned."""
        svc = ApprovalService()
        user_id = uuid4()
        ctx = _make_context(service=svc, user_id=user_id)
        agent = ApprovalAgent(ctx)

        # 1. Agent requests approval
        result = agent.execute(
            {"action": "delete_data", "title": "Delete user data"}
        )
        request_id = result.output["request_id"]
        assert result.status.value == "awaiting_approval"

        # 2. User approves
        from uuid import UUID

        decision = svc.approve(UUID(request_id), user_id=user_id, note="OK")
        assert decision.is_approved is True

        # 3. Verify status
        req = svc.get(UUID(request_id), user_id=user_id)
        assert req.status == ApprovalStatus.APPROVED

    def test_full_flow_rejection(self):
        svc = ApprovalService()
        user_id = uuid4()
        ctx = _make_context(service=svc, user_id=user_id)
        agent = ApprovalAgent(ctx)

        result = agent.execute(
            {"action": "delete_data", "title": "Delete user data"}
        )
        from uuid import UUID

        decision = svc.reject(UUID(result.output["request_id"]), user_id=user_id)
        assert decision.is_rejected is True
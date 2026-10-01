"""Tests for AgentContext."""

from uuid import uuid4

import pytest

from agents.context import AgentBudgets, AgentContext, AgentUsage
from agents.exceptions import AgentBudgetExceededError


class TestAgentContext:
    def test_default_context_has_trace_id(self):
        ctx = AgentContext(user_id=uuid4())
        assert ctx.trace_id is not None
        assert len(ctx.trace_id) > 0

    def test_is_tool_allowed(self):
        ctx = AgentContext(user_id=uuid4(), allowed_tools=frozenset({"a", "b"}))
        assert ctx.is_tool_allowed("a") is True
        assert ctx.is_tool_allowed("c") is False

    def test_step_budget_enforced(self):
        ctx = AgentContext(user_id=uuid4(), budgets=AgentBudgets(max_steps=2))
        ctx.increment_step()
        ctx.increment_step()
        with pytest.raises(AgentBudgetExceededError):
            ctx.check_budget_step()

    def test_tool_budget_enforced(self):
        ctx = AgentContext(user_id=uuid4(), budgets=AgentBudgets(max_tool_calls=1))
        ctx.increment_tool_call()
        with pytest.raises(AgentBudgetExceededError):
            ctx.check_budget_tool()

    def test_time_budget_not_exceeded_immediately(self):
        ctx = AgentContext(user_id=uuid4(), budgets=AgentBudgets(timeout_seconds=60))
        ctx.check_budget_time()  # should not raise

    def test_usage_defaults(self):
        usage = AgentUsage()
        assert usage.steps == 0
        assert usage.tool_calls == 0
        assert usage.total_tokens == 0
        assert usage.elapsed_seconds >= 0
"""Tests for CostTracker and Budget."""

import time

import pytest

from agents.limits.budget import Budget, WorkflowBudget
from agents.limits.cost_tracker import (
    DEFAULT_PRICING,
    CostTracker,
    ModelPricing,
)
from agents.limits.exceptions import BudgetExceededError


# ==========================================================
# CostTracker tests
# ==========================================================


class TestCostTracker:
    def test_records_usage(self):
        t = CostTracker()
        r = t.record(
            user_id="u1",
            agent_name="resume_agent",
            model="gpt-4o-mini",
            prompt_tokens=1000,
            completion_tokens=500,
        )
        assert r.cost_usd > 0
        assert r.user_id == "u1"

    def test_unknown_model_zero_cost(self):
        t = CostTracker()
        r = t.record(
            user_id="u1",
            agent_name="agent",
            model="unknown-model",
            prompt_tokens=1000,
            completion_tokens=1000,
        )
        assert r.cost_usd == 0.0

    def test_user_total(self):
        t = CostTracker()
        t.record(
            user_id="u1",
            agent_name="a",
            model="gpt-4o-mini",
            prompt_tokens=1000,
            completion_tokens=1000,
        )
        t.record(
            user_id="u1",
            agent_name="b",
            model="gpt-4o-mini",
            prompt_tokens=1000,
            completion_tokens=1000,
        )
        assert t.user_total("u1") > 0

    def test_user_total_isolated(self):
        t = CostTracker()
        t.record(
            user_id="u1",
            agent_name="a",
            model="gpt-4o-mini",
            prompt_tokens=1000,
            completion_tokens=1000,
        )
        assert t.user_total("u2") == 0.0

    def test_user_total_tokens(self):
        t = CostTracker()
        t.record(
            user_id="u1",
            agent_name="a",
            model="mock",
            prompt_tokens=100,
            completion_tokens=50,
        )
        assert t.user_total_tokens("u1") == 150

    def test_agent_total(self):
        t = CostTracker()
        t.record(
            user_id="u1",
            agent_name="resume_agent",
            model="gpt-4o-mini",
            prompt_tokens=1000,
            completion_tokens=1000,
        )
        t.record(
            user_id="u2",
            agent_name="resume_agent",
            model="gpt-4o-mini",
            prompt_tokens=1000,
            completion_tokens=1000,
        )
        assert t.agent_total("resume_agent") > 0

    def test_model_total(self):
        t = CostTracker()
        t.record(
            user_id="u1",
            agent_name="a",
            model="gpt-4o",
            prompt_tokens=1_000_000,
            completion_tokens=0,
        )
        # gpt-4o input = $2.50 per 1M tokens
        assert t.model_total("gpt-4o") == pytest.approx(2.50, abs=1e-6)

    def test_custom_pricing(self):
        custom = {"my-model": ModelPricing("my-model", 1.0, 2.0)}
        t = CostTracker(pricing=custom)
        r = t.record(
            user_id="u1",
            agent_name="a",
            model="my-model",
            prompt_tokens=1_000_000,
            completion_tokens=1_000_000,
        )
        assert r.cost_usd == pytest.approx(3.0, abs=1e-6)

    def test_reset(self):
        t = CostTracker()
        t.record(
            user_id="u1",
            agent_name="a",
            model="mock",
            prompt_tokens=100,
            completion_tokens=100,
        )
        t.reset()
        assert t.user_total("u1") == 0.0

    def test_default_pricing_has_expected_models(self):
        assert "gpt-4o-mini" in DEFAULT_PRICING
        assert "claude-3-5-sonnet" in DEFAULT_PRICING


# ==========================================================
# Budget tests
# ==========================================================


class TestBudget:
    def test_default_budget(self):
        b = Budget()
        assert b.max_steps == 12
        assert b.remaining_steps == 12

    def test_add_steps(self):
        b = Budget(max_steps=3)
        b.add_steps(2)
        assert b.remaining_steps == 1

    def test_step_budget_exceeded(self):
        b = Budget(max_steps=2)
        b.add_steps(2)
        with pytest.raises(BudgetExceededError):
            b.add_steps(1)

    def test_tool_call_budget_exceeded(self):
        b = Budget(max_tool_calls=1)
        b.add_tool_calls(1)
        with pytest.raises(BudgetExceededError):
            b.add_tool_calls(1)

    def test_token_budget_exceeded(self):
        b = Budget(max_tokens=100)
        b.add_tokens(100)
        with pytest.raises(BudgetExceededError):
            b.add_tokens(1)

    def test_cost_budget_exceeded(self):
        b = Budget(max_cost_usd=0.001)
        b.add_cost(0.001)
        with pytest.raises(BudgetExceededError):
            b.add_cost(0.001)

    def test_duration_budget_exceeded(self):
        b = Budget(max_duration_seconds=0.05)
        time.sleep(0.06)
        with pytest.raises(BudgetExceededError):
            b.check()

    def test_check_passes_when_within_limits(self):
        b = Budget()
        b.add_steps(1)
        b.check()  # should not raise

    def test_is_exhausted(self):
        b = Budget(max_steps=1)
        assert b.is_exhausted() is False
        b.add_steps(1)  # exactly at limit
        assert b.is_exhausted() is False
        # Simulate exceeding the budget without calling add_steps
        # (add_steps itself raises, which is correct fail-fast behavior)
        b.steps = 2
        assert b.is_exhausted() is True

    def test_remaining_cost_usd(self):
        b = Budget(max_cost_usd=1.0)
        b.add_cost(0.3)
        assert b.remaining_cost_usd == pytest.approx(0.7)


class TestWorkflowBudget:
    def test_for_agent_creates(self):
        wb = WorkflowBudget()
        b1 = wb.for_agent("resume_agent")
        b2 = wb.for_agent("resume_agent")
        assert b1 is b2

    def test_check_all(self):
        wb = WorkflowBudget()
        wb.overall.add_steps(1)
        wb.for_agent("agent1").add_steps(1)
        wb.check_all()  # should not raise

    def test_check_all_raises_on_agent_exceed(self):
        wb = WorkflowBudget()
        agent_budget = wb.for_agent("agent1")
        agent_budget.max_steps = 0
        with pytest.raises(BudgetExceededError):
            wb.for_agent("agent1").add_steps(1)
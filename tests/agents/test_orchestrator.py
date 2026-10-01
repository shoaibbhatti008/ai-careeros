"""Tests for the Orchestrator."""

from typing import Any
from uuid import uuid4

import pytest

from agents.base import BaseAgent
from agents.context import AgentBudgets, AgentContext
from agents.exceptions import AgentError
from agents.orchestrator import Orchestrator
from agents.plan import PlanStatus, PlanStep, WorkflowPlan
from agents.registry import AgentRegistry
from agents.result import AgentResult


# ==========================================================
# Test agents
# ==========================================================


class ProducerAgent(BaseAgent):
    name = "producer"
    description = "Produces a value"

    def run(self, input_data: dict[str, Any]) -> AgentResult:
        return AgentResult.completed(
            {"value": input_data.get("seed", 42), "doubled": input_data.get("seed", 42) * 2}
        )


class ConsumerAgent(BaseAgent):
    name = "consumer"
    description = "Consumes a value"

    def run(self, input_data: dict[str, Any]) -> AgentResult:
        return AgentResult.completed({"received": input_data.get("input_value")})


class FailingAgent(BaseAgent):
    name = "failing"
    description = "Always fails"

    def run(self, input_data: dict[str, Any]) -> AgentResult:
        return AgentResult.failed("intentional failure")


class ApprovalAgent(BaseAgent):
    name = "approval"
    description = "Needs approval"

    def run(self, input_data: dict[str, Any]) -> AgentResult:
        return AgentResult.awaiting_approval(
            approvals=[{"action": "send_email", "to": "user@example.com"}],
            summary="Need approval",
        )


# ==========================================================
# Fixtures
# ==========================================================


@pytest.fixture(autouse=True)
def clean_registry():
    """Clean registry before and after each test."""
    AgentRegistry.clear()
    yield
    AgentRegistry.clear()


@pytest.fixture
def context() -> AgentContext:
    return AgentContext(
        user_id=uuid4(),
        allowed_tools=frozenset(),
    )


@pytest.fixture(autouse=True)
def register_agents():
    """Register test agents."""
    AgentRegistry.register(ProducerAgent)
    AgentRegistry.register(ConsumerAgent)
    AgentRegistry.register(FailingAgent)
    AgentRegistry.register(ApprovalAgent)


# ==========================================================
# Plan tests
# ==========================================================


class TestWorkflowPlan:
    def test_empty_plan_is_invalid(self):
        plan = WorkflowPlan(goal="empty")
        errors = plan.validate()
        assert len(errors) > 0

    def test_valid_single_step_plan(self):
        plan = WorkflowPlan(
            goal="single",
            steps=[PlanStep(step_id="s1", agent_name="producer")],
        )
        assert plan.validate() == []

    def test_duplicate_step_ids_invalid(self):
        plan = WorkflowPlan(
            goal="dup",
            steps=[
                PlanStep(step_id="s1", agent_name="producer"),
                PlanStep(step_id="s1", agent_name="consumer"),
            ],
        )
        errors = plan.validate()
        assert any("duplicate" in e.lower() for e in errors)

    def test_unknown_dependency_invalid(self):
        plan = WorkflowPlan(
            goal="unknown dep",
            steps=[PlanStep(step_id="s1", agent_name="producer", depends_on=["ghost"])],
        )
        errors = plan.validate()
        assert any("unknown step" in e.lower() for e in errors)

    def test_circular_dependency_invalid(self):
        plan = WorkflowPlan(
            goal="cycle",
            steps=[
                PlanStep(step_id="a", agent_name="producer", depends_on=["b"]),
                PlanStep(step_id="b", agent_name="producer", depends_on=["a"]),
            ],
        )
        errors = plan.validate()
        assert any("circular" in e.lower() for e in errors)

    def test_topological_order(self):
        plan = WorkflowPlan(
            goal="topo",
            steps=[
                PlanStep(step_id="c", agent_name="producer", depends_on=["b"]),
                PlanStep(step_id="b", agent_name="producer", depends_on=["a"]),
                PlanStep(step_id="a", agent_name="producer"),
            ],
        )
        ordered = plan.topological_order()
        assert [s.step_id for s in ordered] == ["a", "b", "c"]


# ==========================================================
# Orchestrator tests
# ==========================================================


class TestOrchestrator:
    def test_single_step_plan(self, context):
        plan = WorkflowPlan(
            goal="single",
            steps=[PlanStep(step_id="s1", agent_name="producer", input_data={"seed": 5})],
        )
        result = Orchestrator(context).execute_plan(plan)
        assert result.status.value == "completed"
        assert result.output["step_outputs"]["s1"]["value"] == 5

    def test_multi_step_with_placeholder(self, context):
        plan = WorkflowPlan(
            goal="multi",
            steps=[
                PlanStep(step_id="s1", agent_name="producer", input_data={"seed": 10}),
                PlanStep(
                    step_id="s2",
                    agent_name="consumer",
                    input_data={"input_value": "${s1.doubled}"},
                    depends_on=["s1"],
                ),
            ],
        )
        result = Orchestrator(context).execute_plan(plan)
        assert result.status.value == "completed"
        assert result.output["step_outputs"]["s2"]["received"] == 20

    def test_failing_agent_aborts_plan(self, context):
        plan = WorkflowPlan(
            goal="fail",
            steps=[PlanStep(step_id="s1", agent_name="failing")],
        )
        result = Orchestrator(context).execute_plan(plan)
        assert result.status.value == "failed"
        assert "intentional" in result.error.lower()

    def test_unknown_agent_aborts_plan(self, context):
        plan = WorkflowPlan(
            goal="unknown agent",
            steps=[PlanStep(step_id="s1", agent_name="nonexistent")],
        )
        result = Orchestrator(context).execute_plan(plan)
        assert result.status.value == "failed"

    def test_approval_agent_makes_plan_await(self, context):
        plan = WorkflowPlan(
            goal="approval",
            steps=[PlanStep(step_id="s1", agent_name="approval")],
        )
        result = Orchestrator(context).execute_plan(plan)
        assert result.status.value == "awaiting_approval"
        assert len(result.approvals) == 1

    def test_budget_exceeded_aborts_plan(self):
        ctx = AgentContext(
            user_id=uuid4(),
            budgets=AgentBudgets(max_steps=0),
        )
        plan = WorkflowPlan(
            goal="budget",
            steps=[PlanStep(step_id="s1", agent_name="producer")],
        )
        result = Orchestrator(ctx).execute_plan(plan)
        assert result.status.value == "failed"

    def test_invalid_plan_returns_failed_result(self, context):
        plan = WorkflowPlan(goal="empty", steps=[])
        result = Orchestrator(context).execute_plan(plan)
        assert result.status.value == "failed"

    def test_step_results_inspectable(self, context):
        plan = WorkflowPlan(
            goal="inspect",
            steps=[PlanStep(step_id="s1", agent_name="producer")],
        )
        orch = Orchestrator(context)
        orch.execute_plan(plan)
        assert orch.get_step_result("s1") is not None
        assert "s1" in orch.all_step_results()
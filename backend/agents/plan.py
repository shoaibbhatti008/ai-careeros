"""
WorkflowPlan: structured plan for orchestrator-driven workflows.

A plan is a list of PlanSteps. Each step invokes one agent with
input derived from previous step outputs (via placeholders).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4


class PlanStatus(str, Enum):
    """Status of a plan execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    AWAITING_APPROVAL = "awaiting_approval"
    CANCELLED = "cancelled"


@dataclass
class PlanStep:
    """
    One step in a workflow plan.

    Attributes:
        step_id:      unique identifier within the plan
        agent_name:   which agent to invoke
        input_data:   dict, may contain "${step_id.field}" placeholders
        depends_on:   list of step_ids that must complete first
        description:  human-readable description
    """

    step_id: str
    agent_name: str
    input_data: dict[str, Any] = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    description: str = ""


@dataclass
class WorkflowPlan:
    """
    A complete workflow plan.

    Attributes:
        plan_id:       unique identifier
        goal:          human-readable goal
        steps:         ordered list of PlanStep
        status:        current status
        created_at:    timestamp
        metadata:      free-form metadata
    """

    plan_id: str = field(default_factory=lambda: str(uuid4()))
    goal: str = ""
    steps: list[PlanStep] = field(default_factory=list)
    status: PlanStatus = PlanStatus.PENDING
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> list[str]:
        """
        Validate the plan.

        Returns:
            list of error messages (empty if valid)
        """
        errors: list[str] = []

        if not self.steps:
            errors.append("Plan must have at least one step.")
            return errors

        step_ids = [s.step_id for s in self.steps]
        if len(step_ids) != len(set(step_ids)):
            errors.append("Duplicate step_ids found.")

        step_id_set = set(step_ids)
        for step in self.steps:
            for dep in step.depends_on:
                if dep not in step_id_set:
                    errors.append(f"Step '{step.step_id}' depends on unknown step '{dep}'.")

        # Check for circular dependencies (simple DFS)
        if self._has_cycle():
            errors.append("Circular dependency detected in plan steps.")

        return errors

    def _has_cycle(self) -> bool:
        """Detect cycles in dependency graph."""
        visited: set[str] = set()
        stack: set[str] = set()
        graph = {s.step_id: s.depends_on for s in self.steps}

        def visit(node: str) -> bool:
            if node in stack:
                return True
            if node in visited:
                return False
            visited.add(node)
            stack.add(node)
            for dep in graph.get(node, []):
                if visit(dep):
                    return True
            stack.discard(node)
            return False

        return any(visit(s.step_id) for s in self.steps)

    def get_step(self, step_id: str) -> PlanStep | None:
        """Return the step with the given ID, or None."""
        for step in self.steps:
            if step.step_id == step_id:
                return step
        return None

    def topological_order(self) -> list[PlanStep]:
        """
        Return steps in dependency-safe order.

        Raises:
            ValueError: if the plan has a cycle.
        """
        if self._has_cycle():
            raise ValueError("Cannot topologically order a plan with cycles.")

        ordered: list[PlanStep] = []
        visited: set[str] = set()
        graph = {s.step_id: s for s in self.steps}

        def visit(step_id: str) -> None:
            if step_id in visited:
                return
            step = graph[step_id]
            for dep in step.depends_on:
                visit(dep)
            visited.add(step_id)
            ordered.append(step)

        for step in self.steps:
            visit(step.step_id)

        return ordered

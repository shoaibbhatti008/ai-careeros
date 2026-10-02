"""
Budget enforcement for workflows, agents, and tools.

A Budget has hard limits:
- max_steps
- max_tool_calls
- max_tokens
- max_cost_usd
- max_duration_seconds

Budgets can be nested: a WorkflowBudget contains a per-agent budget.
"""

import time
from dataclasses import dataclass, field

from agents.limits.exceptions import BudgetExceededError


@dataclass
class Budget:
    """A hard budget for a unit of work."""

    max_steps: int = 12
    max_tool_calls: int = 20
    max_tokens: int = 8192
    max_cost_usd: float = 1.0
    max_duration_seconds: float = 120.0

    # Tracked usage
    steps: int = 0
    tool_calls: int = 0
    tokens: int = 0
    cost_usd: float = 0.0
    started_at: float = field(default_factory=time.monotonic)

    # ==========================================================
    # Increment
    # ==========================================================

    def add_steps(self, n: int = 1) -> None:
        self.steps += n
        self._check_steps()

    def add_tool_calls(self, n: int = 1) -> None:
        self.tool_calls += n
        self._check_tool_calls()

    def add_tokens(self, n: int) -> None:
        self.tokens += n
        self._check_tokens()

    def add_cost(self, cost_usd: float) -> None:
        self.cost_usd += cost_usd
        self._check_cost()

    # ==========================================================
    # Check (raises)
    # ==========================================================

    def check(self) -> None:
        """Raise if any budget is exceeded."""
        self._check_steps()
        self._check_tool_calls()
        self._check_tokens()
        self._check_cost()
        self._check_duration()

    def is_exhausted(self) -> bool:
        """Return True if any budget is exceeded (without raising)."""
        try:
            self.check()
            return False
        except BudgetExceededError:
            return True

    # ==========================================================
    # Remaining
    # ==========================================================

    @property
    def remaining_steps(self) -> int:
        return max(0, self.max_steps - self.steps)

    @property
    def remaining_tool_calls(self) -> int:
        return max(0, self.max_tool_calls - self.tool_calls)

    @property
    def remaining_tokens(self) -> int:
        return max(0, self.max_tokens - self.tokens)

    @property
    def remaining_cost_usd(self) -> float:
        return max(0.0, self.max_cost_usd - self.cost_usd)

    @property
    def elapsed_seconds(self) -> float:
        return time.monotonic() - self.started_at

    @property
    def remaining_seconds(self) -> float:
        return max(0.0, self.max_duration_seconds - self.elapsed_seconds)

    # ==========================================================
    # Internal checks
    # ==========================================================

    def _check_steps(self) -> None:
        if self.steps > self.max_steps:
            raise BudgetExceededError(f"Step budget exceeded ({self.steps} > {self.max_steps}).")

    def _check_tool_calls(self) -> None:
        if self.tool_calls > self.max_tool_calls:
            raise BudgetExceededError(
                f"Tool-call budget exceeded ({self.tool_calls} > {self.max_tool_calls})."
            )

    def _check_tokens(self) -> None:
        if self.tokens > self.max_tokens:
            raise BudgetExceededError(f"Token budget exceeded ({self.tokens} > {self.max_tokens}).")

    def _check_cost(self) -> None:
        if self.cost_usd > self.max_cost_usd:
            raise BudgetExceededError(
                f"Cost budget exceeded (${self.cost_usd:.4f} > ${self.max_cost_usd:.4f})."
            )

    def _check_duration(self) -> None:
        if self.elapsed_seconds > self.max_duration_seconds:
            raise BudgetExceededError(
                f"Time budget exceeded "
                f"({self.elapsed_seconds:.1f}s > {self.max_duration_seconds:.1f}s)."
            )


@dataclass
class WorkflowBudget:
    """
    A hierarchical budget for multi-step workflows.

    Contains:
    - overall: the total budget
    - per_agent: optional per-agent budgets (reset per agent run)
    """

    overall: Budget = field(default_factory=Budget)
    per_agent: dict[str, Budget] = field(default_factory=dict)

    def for_agent(self, agent_name: str) -> Budget:
        """Return (creating if needed) the budget for a specific agent."""
        if agent_name not in self.per_agent:
            self.per_agent[agent_name] = Budget()
        return self.per_agent[agent_name]

    def check_all(self) -> None:
        """Check overall + all agent budgets."""
        self.overall.check()
        for b in self.per_agent.values():
            b.check()

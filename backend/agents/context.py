"""
AgentContext: per-execution context passed to every agent.

The context is the ONLY channel through which an agent can access:
- The current user (as an opaque ID)
- The database (via injected callables, NOT direct ORM)
- Budgets (max steps, max tool calls, timeout)
- Tool allowlist
- Trace ID

Agents MUST NOT access Django ORM, filesystem, or environment directly.
All external access goes through injected, permission-checked tools.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass
class AgentBudgets:
    """Execution budgets — hard limits enforced by BaseAgent."""

    max_steps: int = 12
    max_tool_calls: int = 20
    timeout_seconds: int = 120
    max_tokens: int = 8192


@dataclass
class AgentUsage:
    """Tracked usage during execution."""

    steps: int = 0
    tool_calls: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    @property
    def elapsed_seconds(self) -> float:
        return (datetime.now(UTC) - self.started_at).total_seconds()


@dataclass
class AgentContext:
    """
    Context for one agent execution.

    Attributes:
        user_id:             Opaque user identifier.
        trace_id:            Unique ID for this execution (for logs/audit).
        budgets:             Hard execution limits.
        allowed_tools:       Explicit allowlist of tool names.
        tool_executor:       Callable that runs a tool.
        metadata:            Free-form per-request metadata.
        log:                 Structured logger callable.
    """

    user_id: UUID
    trace_id: str = field(default_factory=lambda: str(uuid4()))
    budgets: AgentBudgets = field(default_factory=AgentBudgets)
    allowed_tools: frozenset[str] = field(default_factory=frozenset)
    tool_executor: Callable[..., dict[str, Any]] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    log: Callable[[str, dict[str, Any]], None] = field(default=lambda msg, extra=None: None)
    usage: AgentUsage = field(default_factory=AgentUsage)

    def is_tool_allowed(self, tool_name: str) -> bool:
        """Return True if the agent is allowed to call this tool."""
        return tool_name in self.allowed_tools

    def check_budget_step(self) -> None:
        from agents.exceptions import AgentBudgetExceededError

        if self.usage.steps >= self.budgets.max_steps:
            raise AgentBudgetExceededError(f"Step budget exceeded (max={self.budgets.max_steps})")

    def check_budget_tool(self) -> None:
        from agents.exceptions import AgentBudgetExceededError

        if self.usage.tool_calls >= self.budgets.max_tool_calls:
            raise AgentBudgetExceededError(
                f"Tool-call budget exceeded (max={self.budgets.max_tool_calls})"
            )

    def check_budget_time(self) -> None:
        from agents.exceptions import AgentBudgetExceededError

        if self.usage.elapsed_seconds > self.budgets.timeout_seconds:
            raise AgentBudgetExceededError(
                f"Time budget exceeded (max={self.budgets.timeout_seconds}s)"
            )

    def check_all_budgets(self) -> None:
        self.check_budget_step()
        self.check_budget_tool()
        self.check_budget_time()

    def increment_step(self) -> None:
        self.usage.steps += 1

    def increment_tool_call(self) -> None:
        self.usage.tool_calls += 1

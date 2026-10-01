"""
BaseAgent: abstract base class for all agents.

Design principles:
1. Agents are PURE: they receive AgentContext + input, return AgentResult.
2. Agents NEVER access the DB, filesystem, or environment directly.
3. All external access goes through the tool executor (permission-checked).
4. Budgets are enforced by the framework, not by the agent.
5. Outputs are validated against a declared schema.
"""

from abc import ABC, abstractmethod
from typing import Any, ClassVar

from agents.context import AgentContext
from agents.exceptions import (
    AgentPermissionError,
    AgentToolNotAllowedError,
    AgentValidationError,
)
from agents.result import AgentResult, AgentStatus


class BaseAgent(ABC):
    """
    Abstract base for all agents.

    Subclasses MUST implement:
        name:                 unique agent name (e.g. "resume_agent")
        description:          what this agent does
        allowed_tools:        frozenset of tool names this agent may call
        input_schema:         dict describing expected input (informational)
        output_schema:        dict describing produced output (informational)
        run():                main logic

    The framework will:
    - Validate the agent's name is unique
    - Enforce tool allowlist
    - Enforce budgets
    - Catch and wrap errors into AgentResult
    """

    name: ClassVar[str]
    description: ClassVar[str] = ""
    allowed_tools: ClassVar[frozenset[str]] = frozenset()
    input_schema: ClassVar[dict[str, Any]] = {}
    output_schema: ClassVar[dict[str, Any]] = {}

    def __init__(self, context: AgentContext) -> None:
        if not getattr(self, "name", None):
            raise AgentValidationError(
                f"{self.__class__.__name__} must define a class-level 'name' attribute."
            )
        self.context = context

    # ==========================================================
    # Tool invocation (permission-checked)
    # ==========================================================

    def call_tool(self, tool_name: str, **kwargs: Any) -> dict[str, Any]:
        """
        Call a tool by name with permission checks.

        Raises:
            AgentToolNotAllowedError: tool not in agent's allowlist
            AgentPermissionError:     tool not permitted in current context
            AgentBudgetExceededError: tool-call budget exceeded
        """
        # 1. Agent-level allowlist
        if tool_name not in self.allowed_tools:
            raise AgentToolNotAllowedError(
                f"Agent '{self.name}' is not allowed to use tool '{tool_name}'.",
                agent_name=self.name,
            )

        # 2. Context-level allowlist (per-request)
        if not self.context.is_tool_allowed(tool_name):
            raise AgentPermissionError(
                f"Tool '{tool_name}' is not permitted in this context.",
                agent_name=self.name,
            )

        # 3. Budget check
        self.context.check_budget_tool()

        # 4. Executor must be injected
        if self.context.tool_executor is None:
            raise AgentPermissionError(
                "No tool executor was injected into the context.",
                agent_name=self.name,
            )

        # 5. Execute
        self.context.increment_tool_call()
        result = self.context.tool_executor(tool_name, **kwargs)
        if not isinstance(result, dict):
            raise AgentValidationError(
                f"Tool '{tool_name}' returned a non-dict result.",
                agent_name=self.name,
            )
        return result

    # ==========================================================
    # Main entry point
    # ==========================================================

    def execute(self, input_data: dict[str, Any]) -> AgentResult:
        """
        Framework-controlled execution.

        - Enforces budgets
        - Catches exceptions and returns AgentResult
        - Logs start and end
        """
        self.context.log(
            f"agent_start:{self.name}",
            {"input_keys": list(input_data.keys()), "trace_id": self.context.trace_id},
        )

        try:
            self.context.check_all_budgets()
            result = self.run(input_data)
            if not isinstance(result, AgentResult):
                raise AgentValidationError(
                    f"Agent '{self.name}' returned {type(result).__name__}, "
                    "expected AgentResult.",
                    agent_name=self.name,
                )
            self.context.log(
                f"agent_end:{self.name}",
                {
                    "status": result.status.value,
                    "steps": self.context.usage.steps,
                    "tool_calls": self.context.usage.tool_calls,
                    "elapsed_seconds": round(self.context.usage.elapsed_seconds, 3),
                },
            )
            return result

        except AgentValidationError as exc:
            self.context.log(f"agent_error:{self.name}", {"error": str(exc)})
            return AgentResult.failed(str(exc))
        except Exception as exc:
            # Catch-all: never let an agent crash the request.
            self.context.log(
                f"agent_unhandled_error:{self.name}",
                {"error": str(exc), "type": type(exc).__name__},
            )
            return AgentResult(
                status=AgentStatus.FAILED,
                error=f"Unhandled error in agent '{self.name}': {exc}",
            )

    @abstractmethod
    def run(self, input_data: dict[str, Any]) -> AgentResult:
        """
        Agent logic. Must return AgentResult.

        Agents should:
        - Read inputs from input_data
        - Use self.call_tool() to access external resources
        - Use self.context.log() for observability
        - Return AgentResult.completed(...) or .failed(...) or .awaiting_approval(...)
        """
        raise NotImplementedError

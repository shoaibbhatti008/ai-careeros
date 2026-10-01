"""Tests for BaseAgent."""

from typing import Any

import pytest

from agents.base import BaseAgent
from agents.context import AgentBudgets, AgentContext
from agents.exceptions import (
    AgentToolNotAllowedError,
)
from agents.result import AgentResult, AgentStatus

# ==========================================================
# Test agents
# ==========================================================


class EchoAgent(BaseAgent):
    """Returns whatever it receives."""

    name = "echo"
    description = "Echoes input"
    allowed_tools = frozenset()

    def run(self, input_data: dict[str, Any]) -> AgentResult:
        return AgentResult.completed({"echo": input_data}, "echoed")


class ToolUsingAgent(BaseAgent):
    """Calls a tool."""

    name = "tool_user"
    description = "Uses a tool"
    allowed_tools = frozenset({"greet"})

    def run(self, input_data: dict[str, Any]) -> AgentResult:
        result = self.call_tool("greet", name=input_data.get("name", "world"))
        return AgentResult.completed(result)


class BadToolAgent(BaseAgent):
    """Tries to use a tool it's not allowed to use."""

    name = "bad_tool_user"
    description = "Tries to use a forbidden tool"
    allowed_tools = frozenset()

    def run(self, input_data: dict[str, Any]) -> AgentResult:
        return AgentResult.completed(self.call_tool("danger"))


class CrashingAgent(BaseAgent):
    """Crashes."""

    name = "crasher"
    description = "Raises"
    allowed_tools = frozenset()

    def run(self, input_data: dict[str, Any]) -> AgentResult:
        raise RuntimeError("Boom")


# ==========================================================
# Fixtures
# ==========================================================


def _make_context(**overrides: Any) -> AgentContext:
    from uuid import uuid4

    def default_tool_executor(tool_name: str, **kwargs: Any) -> dict[str, Any]:
        """Default test tool executor.

        IMPORTANT: The first positional arg must be `tool_name`, because
        BaseAgent.call_tool() passes the tool name positionally.
        """
        return {"tool": tool_name, "kwargs": kwargs}

    defaults = {
        "user_id": uuid4(),
        "allowed_tools": frozenset({"greet"}),
        "tool_executor": default_tool_executor,
    }
    defaults.update(overrides)
    return AgentContext(**defaults)

# ==========================================================
# Tests
# ==========================================================


class TestBaseAgent:
    def test_agent_requires_name(self):
        class NamelessAgent(BaseAgent):
            def run(self, input_data):
                return AgentResult.completed({})

        with pytest.raises(Exception):
            NamelessAgent(_make_context())

    def test_echo_agent_completes(self):
        agent = EchoAgent(_make_context())
        result = agent.execute({"hello": "world"})
        assert result.status == AgentStatus.COMPLETED
        assert result.output == {"echo": {"hello": "world"}}

    def test_agent_with_allowed_tool_succeeds(self):
        agent = ToolUsingAgent(_make_context())
        result = agent.execute({"name": "Ali"})
        assert result.status == AgentStatus.COMPLETED
        assert result.output["tool"] == "greet"
        assert result.output["kwargs"]["name"] == "Ali"

    def test_agent_blocked_when_tool_not_in_allowlist(self):
        agent = BadToolAgent(_make_context())
        result = agent.execute({})
        assert result.status == AgentStatus.FAILED
        assert "not allowed" in result.error.lower()

    def test_agent_blocked_when_tool_not_in_context(self):
        ctx = _make_context(allowed_tools=frozenset())  # empty context allowlist
        agent = ToolUsingAgent(ctx)
        result = agent.execute({})
        assert result.status == AgentStatus.FAILED

    def test_agent_blocked_when_no_tool_executor(self):
        ctx = _make_context(tool_executor=None)
        agent = ToolUsingAgent(ctx)
        result = agent.execute({})
        assert result.status == AgentStatus.FAILED

    def test_agent_handles_unhandled_exception(self):
        agent = CrashingAgent(_make_context())
        result = agent.execute({})
        assert result.status == AgentStatus.FAILED
        assert "Unhandled error" in result.error

    def test_agent_respects_tool_budget(self):
        ctx = _make_context(budgets=AgentBudgets(max_tool_calls=1))
        agent = ToolUsingAgent(ctx)
        agent.execute({})  # 1st call succeeds
        # 2nd call should exceed
        result = agent.execute({})
        # Still OK because budget resets? No — usage persists on context.
        # Actually usage is on context, so 2nd call fails.
        assert result.status == AgentStatus.FAILED
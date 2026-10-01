"""Tests for the tool framework."""

from typing import Any

import pytest

from agents.tools.base import BaseTool, RiskLevel, ToolContext, ToolResult
from agents.tools.errors import (
    ToolInputError,
    ToolNotAllowedError,
    ToolNotFoundError,
)
from agents.tools.registry import ToolRegistry, execute_tool, register_tool


# ==========================================================
# Test tools
# ==========================================================


@register_tool
class SimpleTool(BaseTool):
    name = "simple"
    description = "Returns a fixed value."
    risk_level = RiskLevel.LOW
    allowed_agents = frozenset({"test_agent"})

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        return {"value": 42}


@register_tool
class InputValidatingTool(BaseTool):
    name = "validating"
    description = "Requires a 'name' field."
    allowed_agents = frozenset()
    input_schema = {"required": ["name"]}

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        return {"greeting": f"Hello, {input_data['name']}"}


@register_tool
class CrashingTool(BaseTool):
    name = "crashing"
    description = "Always raises."
    allowed_agents = frozenset()

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        raise RuntimeError("Boom")


@register_tool
class ApprovalTool(BaseTool):
    name = "requires_approval"
    description = "Needs approval."
    allowed_agents = frozenset()
    requires_approval = True

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        return {"done": True}


# ==========================================================
# Fixtures
# ==========================================================


@pytest.fixture(autouse=True)
def clean_registry():
    """Preserve and restore registry around each test."""
    saved = dict(ToolRegistry._tools)
    yield
    ToolRegistry._tools = saved


# ==========================================================
# Tests
# ==========================================================


class TestToolRegistry:
    def test_register_and_get(self):
        tool_cls = ToolRegistry.get("simple")
        assert tool_cls is SimpleTool

    def test_get_unknown_raises(self):
        with pytest.raises(ToolNotFoundError):
            ToolRegistry.get("nonexistent")

    def test_has(self):
        assert ToolRegistry.has("simple") is True
        assert ToolRegistry.has("nonexistent") is False

    def test_list_tools(self):
        tools = ToolRegistry.list_tools()
        assert "simple" in tools
        assert tools["simple"]["risk_level"] == "low"

    def test_duplicate_registration_raises(self):
        with pytest.raises(ValueError):

            @register_tool
            class SimpleTool2(BaseTool):
                name = "simple"  # duplicate

                def run(self, input_data):
                    return {}


class TestToolExecution:
    def test_simple_tool_succeeds(self):
        tool = SimpleTool(ToolContext(user_id="u1"))
        result = tool.execute({})
        assert result.success is True
        assert result.data == {"value": 42}

    def test_input_validation_requires_fields(self):
        tool = InputValidatingTool(ToolContext(user_id="u1"))
        result = tool.execute({})  # missing 'name'
        assert result.success is False
        assert "name" in result.error.lower()

    def test_input_validation_passes_when_provided(self):
        tool = InputValidatingTool(ToolContext(user_id="u1"))
        result = tool.execute({"name": "Ali"})
        assert result.success is True
        assert result.data["greeting"] == "Hello, Ali"

    def test_crashing_tool_is_wrapped(self):
        tool = CrashingTool(ToolContext(user_id="u1"))
        result = tool.execute({})
        assert result.success is False
        assert "Unhandled error" in result.error

    def test_approval_required_blocks_execution(self):
        tool = ApprovalTool(ToolContext(user_id="u1"))
        result = tool.execute({})
        assert result.success is False
        assert "approval" in result.error.lower()

    def test_approval_granted_allows_execution(self):
        tool = ApprovalTool(ToolContext(user_id="u1", approval_granted=True))
        result = tool.execute({})
        assert result.success is True
        assert result.data == {"done": True}


class TestExecuteToolHelper:
    def test_executes_when_all_checks_pass(self):
        result = execute_tool(
            tool_name="simple",
            agent_name="test_agent",
            agent_allowed_tools=frozenset({"simple"}),
            context_allowed_tools=frozenset({"simple"}),
            input_data={},
            tool_context=ToolContext(user_id="u1"),
        )
        assert result["value"] == 42

    def test_blocked_when_tool_not_in_agent_allowlist(self):
        with pytest.raises(ToolNotAllowedError):
            execute_tool(
                tool_name="simple",
                agent_name="test_agent",
                agent_allowed_tools=frozenset(),  # empty
                context_allowed_tools=frozenset({"simple"}),
                input_data={},
                tool_context=ToolContext(user_id="u1"),
            )

    def test_blocked_when_tool_not_in_context_allowlist(self):
        with pytest.raises(ToolNotAllowedError):
            execute_tool(
                tool_name="simple",
                agent_name="test_agent",
                agent_allowed_tools=frozenset({"simple"}),
                context_allowed_tools=frozenset(),  # empty
                input_data={},
                tool_context=ToolContext(user_id="u1"),
            )

    def test_blocked_when_agent_not_in_tool_allowlist(self):
        with pytest.raises(ToolNotAllowedError):
            execute_tool(
                tool_name="simple",
                agent_name="some_other_agent",  # not in SimpleTool.allowed_agents
                agent_allowed_tools=frozenset({"simple"}),
                context_allowed_tools=frozenset({"simple"}),
                input_data={},
                tool_context=ToolContext(user_id="u1"),
            )
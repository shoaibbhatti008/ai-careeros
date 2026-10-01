"""
ToolRegistry: central registry of all available tools.

Agents can only call tools that are:
1. Registered in the ToolRegistry
2. In the agent's `allowed_tools` allowlist
3. In the AgentContext's `allowed_tools` allowlist
4. Permitted by the tool's `allowed_agents` list
"""

from typing import Any

from agents.tools.base import BaseTool, ToolContext, ToolResult
from agents.tools.errors import (
    ToolNotAllowedError,
    ToolNotFoundError,
)


class ToolRegistry:
    """Central registry of tools."""

    _tools: dict[str, type[BaseTool]] = {}

    @classmethod
    def register(cls, tool_cls: type[BaseTool]) -> type[BaseTool]:
        name = getattr(tool_cls, "name", None)
        if not name:
            raise ValueError(f"Cannot register {tool_cls.__name__}: missing 'name' attribute.")
        if name in cls._tools:
            raise ValueError(f"Tool '{name}' is already registered.")
        cls._tools[name] = tool_cls
        return tool_cls

    @classmethod
    def get(cls, name: str) -> type[BaseTool]:
        if name not in cls._tools:
            raise ToolNotFoundError(f"Tool '{name}' is not registered.")
        return cls._tools[name]

    @classmethod
    def has(cls, name: str) -> bool:
        return name in cls._tools

    @classmethod
    def list_tools(cls) -> dict[str, dict[str, Any]]:
        return {
            name: {
                "name": name,
                "description": cls._tools[name].description,
                "risk_level": cls._tools[name].risk_level.value,
                "allowed_agents": sorted(cls._tools[name].allowed_agents),
                "requires_approval": cls._tools[name].requires_approval,
            }
            for name in cls._tools
        }

    @classmethod
    def clear(cls) -> None:
        cls._tools.clear()


def register_tool(tool_cls: type[BaseTool]) -> type[BaseTool]:
    """Decorator to register a tool class."""
    return ToolRegistry.register(tool_cls)


# ==========================================================
# Safe tool executor (used by BaseAgent.call_tool)
# ==========================================================


def execute_tool(
    *,
    tool_name: str,
    agent_name: str,
    agent_allowed_tools: frozenset[str],
    context_allowed_tools: frozenset[str],
    input_data: dict[str, Any],
    tool_context: ToolContext,
) -> dict[str, Any]:
    """
    Execute a tool with full permission checks.

    This is the ONLY way agents should invoke tools.
    Returns the tool's output dict on success.
    Raises ToolError subclasses on failure.

    Checks performed (in order):
    1. Tool is registered
    2. Tool is in agent's allowlist
    3. Tool is in context's allowlist
    4. Agent is in tool's allowed_agents list
    """
    # 1. Registered
    tool_cls = ToolRegistry.get(tool_name)

    # 2. Agent allowlist
    if tool_name not in agent_allowed_tools:
        raise ToolNotAllowedError(
            f"Agent '{agent_name}' is not allowed to use tool '{tool_name}'.",
            tool_name=tool_name,
        )

    # 3. Context allowlist
    if tool_name not in context_allowed_tools:
        raise ToolNotAllowedError(
            f"Tool '{tool_name}' is not permitted in this context.",
            tool_name=tool_name,
        )

    # 4. Tool's own allowlist
    if tool_cls.allowed_agents and agent_name not in tool_cls.allowed_agents:
        raise ToolNotAllowedError(
            f"Tool '{tool_name}' does not permit agent '{agent_name}'.",
            tool_name=tool_name,
        )

    # Execute
    tool = tool_cls(tool_context)
    result: ToolResult = tool.execute(input_data)
    if not result.success:
        from agents.tools.errors import ToolExecutionError

        raise ToolExecutionError(result.error, tool_name=tool_name)

    return result.data

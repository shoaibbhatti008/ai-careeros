"""Controlled tool framework for agents.

Tools are the ONLY way agents can affect the outside world.
Every tool must:
- Be registered in the ToolRegistry
- Declare its risk level
- Declare which agents may use it
- Validate inputs against a schema
- Have a timeout and rate limit
- Return structured output

Agents cannot create or invoke tools that are not registered.
"""

from agents.tools.base import BaseTool, ToolContext, ToolResult
from agents.tools.errors import (
    ToolError,
    ToolExecutionError,
    ToolInputError,
    ToolNotAllowedError,
    ToolNotFoundError,
    ToolOutputError,
    ToolPermissionError,
    ToolRateLimitError,
    ToolTimeoutError,
)
from agents.tools.registry import ToolRegistry, register_tool

__all__ = [
    "BaseTool",
    "ToolContext",
    "ToolResult",
    "ToolRegistry",
    "register_tool",
    "ToolError",
    "ToolNotFoundError",
    "ToolNotAllowedError",
    "ToolPermissionError",
    "ToolInputError",
    "ToolOutputError",
    "ToolExecutionError",
    "ToolTimeoutError",
    "ToolRateLimitError",
]

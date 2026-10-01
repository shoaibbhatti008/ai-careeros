"""
ApprovalAgent: requests human approval for a proposed action.

The agent NEVER executes the action itself. It only creates the
approval request. The caller is responsible for:
1. Waiting for approval
2. Executing the action only if approved

This separates "proposal" from "execution" — a core safety principle.
"""

from typing import Any

from agents.base import BaseAgent
from agents.registry import register_agent
from agents.result import AgentResult, AgentStatus


@register_agent
class ApprovalAgent(BaseAgent):
    """Creates human approval requests for sensitive actions."""

    name = "approval_agent"
    description = "Requests human approval before sensitive actions."
    allowed_tools = frozenset({"request_approval"})

    input_schema = {
        "type": "object",
        "properties": {
            "action": {"type": "string"},
            "title": {"type": "string"},
            "description": {"type": "string"},
            "payload": {"type": "object"},
            "expires_in_hours": {"type": "integer"},
        },
        "required": ["action", "title"],
    }

    output_schema = {
        "type": "object",
        "properties": {
            "request_id": {"type": "string"},
            "status": {"type": "string"},
            "action": {"type": "string"},
            "title": {"type": "string"},
        },
    }

    def run(self, input_data: dict[str, Any]) -> AgentResult:
        action = input_data.get("action")
        title = input_data.get("title")
        if not action or not title:
            return AgentResult.failed("action and title are required.")

        # Forward the request to the tool
        tool_input: dict[str, Any] = {
            "action": action,
            "title": title,
            "agent_name": self.name,
        }
        for key in ("description", "payload", "expires_in_hours"):
            if key in input_data:
                tool_input[key] = input_data[key]

        result = self.call_tool("request_approval", **tool_input)

        return AgentResult(
            status=AgentStatus.AWAITING_APPROVAL,
            output={
                "request_id": result["request_id"],
                "status": result["status"],
                "action": result["action"],
                "title": result["title"],
            },
            summary=f"Awaiting approval for: {title}",
            approvals=[
                {
                    "request_id": result["request_id"],
                    "action": result["action"],
                    "title": result["title"],
                }
            ],
            usage={
                "steps": self.context.usage.steps,
                "tool_calls": self.context.usage.tool_calls,
            },
        )

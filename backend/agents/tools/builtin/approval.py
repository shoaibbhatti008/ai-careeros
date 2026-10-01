"""
RequestApprovalTool: request user approval before a sensitive action.

Risk: LOW (creates a request; does not execute anything).
The actual action is executed by the caller AFTER approval.
"""

from typing import Any, ClassVar
from uuid import UUID

from agents.approval.service import ApprovalService
from agents.approval.types import ApprovalAction
from agents.tools.base import BaseTool, RiskLevel


class RequestApprovalTool(BaseTool):
    """
    Create an approval request.

    Input:
        action:       str (one of ApprovalAction values)
        title:        str
        description:  str
        payload:      dict
        expires_in_hours: int (optional)

    Output:
        request_id:   str (UUID)
        status:       str
        title:        str
    """

    name = "request_approval"
    description = "Creates a human approval request before a sensitive action."
    risk_level: ClassVar[RiskLevel] = RiskLevel.LOW
    allowed_agents: ClassVar[frozenset[str]] = frozenset({"approval_agent"})
    input_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "action": {"type": "string"},
            "title": {"type": "string"},
        },
        "required": ["action", "title"],
    }
    output_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "request_id": {"type": "string"},
            "status": {"type": "string"},
            "title": {"type": "string"},
        },
    }
    timeout_seconds = 5
    rate_limit_per_minute = 300

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        service = self.context.metadata.get("approval_service")
        if service is None or not isinstance(service, ApprovalService):
            from agents.tools.errors import ToolExecutionError

            raise ToolExecutionError(
                "No ApprovalService was injected in " "ToolContext.metadata['approval_service'].",
                tool_name=self.name,
            )

        agent_name = input_data.get("agent_name") or self.context.metadata.get(
            "agent_name", "unknown"
        )
        action_str = input_data["action"]

        try:
            action = ApprovalAction(action_str)
        except ValueError:
            from agents.tools.errors import ToolInputError

            raise ToolInputError(
                f"Unknown action '{action_str}'. Valid: " f"{[a.value for a in ApprovalAction]}",
                tool_name=self.name,
            ) from None

        expires_in_hours = input_data.get("expires_in_hours")
        expires_at = None
        if expires_in_hours:
            from agents.approval.types import default_expiry

            expires_at = default_expiry(hours=int(expires_in_hours))

        request = service.create_request(
            user_id=UUID(self.context.user_id),
            agent_name=agent_name,
            action=action,
            title=input_data["title"],
            description=input_data.get("description", ""),
            payload=input_data.get("payload", {}),
            expires_at=expires_at,
        )

        return {
            "request_id": str(request.request_id),
            "status": request.status.value,
            "title": request.title,
            "action": request.action.value,
        }

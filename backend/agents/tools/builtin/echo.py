"""Echo tool: returns the input. Used for testing agent-tool integration."""

from typing import Any, ClassVar

from agents.tools.base import BaseTool, RiskLevel


class EchoTool(BaseTool):
    """Echoes its input back."""

    name = "echo"
    description = "Echoes the input back."
    risk_level: ClassVar[RiskLevel] = RiskLevel.LOW
    allowed_agents: ClassVar[frozenset[str]] = frozenset()
    input_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {"message": {"type": "string"}},
    }
    output_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {"echo": {"type": "string"}},
    }
    timeout_seconds = 5
    rate_limit_per_minute = 1000
    requires_approval = False

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        return {"echo": input_data.get("message", "")}

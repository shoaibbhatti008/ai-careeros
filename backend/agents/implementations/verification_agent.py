"""
VerificationAgent: verifies another agent's output.

The agent does NOT know which agent produced the output. It receives
structured data and runs a rule set against it.
"""

from typing import Any

from agents.base import BaseAgent
from agents.registry import register_agent
from agents.result import AgentResult, AgentStatus


@register_agent
class VerificationAgent(BaseAgent):
    """Runs deterministic verification on arbitrary structured data."""

    name = "verification_agent"
    description = "Verifies structured data against required fields and schema rules."
    allowed_tools = frozenset({"verify_output"})

    input_schema = {
        "type": "object",
        "properties": {
            "data": {"type": "object"},
            "required_fields": {"type": "array"},
            "schema": {"type": "object"},
            "min_confidence": {"type": "number"},
            "allow_pii": {"type": "boolean"},
        },
        "required": ["data"],
    }

    output_schema = {
        "type": "object",
        "properties": {
            "passed": {"type": "boolean"},
            "errors": {"type": "array"},
            "warnings": {"type": "array"},
            "summary": {"type": "string"},
        },
    }

    def run(self, input_data: dict[str, Any]) -> AgentResult:
        data = input_data.get("data")
        if not isinstance(data, dict):
            return AgentResult.failed("data must be a dict.")

        tool_input: dict[str, Any] = {"data": data}
        for key in ("required_fields", "schema", "min_confidence", "allow_pii"):
            if key in input_data:
                tool_input[key] = input_data[key]

        verification = self.call_tool("verify_output", **tool_input)

        passed = bool(verification.get("passed", False))
        errors = list(verification.get("errors", []) or [])
        warnings = list(verification.get("warnings", []) or [])
        summary = verification.get("summary", "")

        output = {
            "passed": passed,
            "errors": errors,
            "warnings": warnings,
            "summary": summary,
        }

        if passed:
            return AgentResult(
                status=AgentStatus.COMPLETED,
                output=output,
                summary=summary or "Verification passed.",
                usage={
                    "steps": self.context.usage.steps,
                    "tool_calls": self.context.usage.tool_calls,
                },
            )

        return AgentResult(
            status=AgentStatus.FAILED,
            output=output,
            error="Verification failed: " + "; ".join(errors),
            summary=summary,
        )

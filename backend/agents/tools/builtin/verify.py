"""
VerifyOutputTool: run the Verifier on arbitrary data.

Risk: LOW. Pure computation. No external access.
"""

from typing import Any, ClassVar

from agents.tools.base import BaseTool, RiskLevel
from agents.verification.verifier import Verifier


class VerifyOutputTool(BaseTool):
    """
    Verify a data payload against a set of rules.

    Input:
        data:             dict
        required_fields:  list[str] (optional)
        schema:           dict (optional)
        min_confidence:   float (optional)
        allow_pii:        bool (optional, default False)

    Output:
        passed:   bool
        errors:   list[str]
        warnings: list[str]
        summary:  str
    """

    name = "verify_output"
    description = "Runs deterministic verification checks on structured output."
    risk_level: ClassVar[RiskLevel] = RiskLevel.LOW
    allowed_agents: ClassVar[frozenset[str]] = frozenset({"verification_agent"})
    input_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {"data": {"type": "object"}},
        "required": ["data"],
    }
    output_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "passed": {"type": "boolean"},
            "errors": {"type": "array"},
            "warnings": {"type": "array"},
            "summary": {"type": "string"},
        },
    }
    timeout_seconds = 10
    rate_limit_per_minute = 300

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        data = input_data["data"]
        required = input_data.get("required_fields") or []
        schema = input_data.get("schema")
        min_conf = input_data.get("min_confidence")
        allow_pii = bool(input_data.get("allow_pii", False))

        verifier = Verifier(
            required_fields=required,
            schema=schema,
            min_confidence=min_conf,
            allow_pii=allow_pii,
        )
        report = verifier.verify(data)

        return {
            "passed": report.passed,
            "errors": report.errors,
            "warnings": report.warnings,
            "summary": report.summary(),
        }

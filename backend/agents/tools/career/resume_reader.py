"""
ResumeReaderTool: reads and normalizes resume text.

Risk: LOW. Pure text processing. No external access.
"""

from typing import Any, ClassVar

from agents.tools.base import BaseTool, RiskLevel


class ResumeReaderTool(BaseTool):
    """Read a resume's raw text and return basic stats."""

    name = "resume_reader"
    description = "Reads a resume's raw text and returns word/char counts and normalized text."
    risk_level: ClassVar[RiskLevel] = RiskLevel.LOW
    allowed_agents: ClassVar[frozenset[str]] = frozenset({"resume_agent"})
    input_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "resume_text": {"type": "string"},
        },
        "required": ["resume_text"],
    }
    output_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "normalized_text": {"type": "string"},
            "word_count": {"type": "integer"},
            "char_count": {"type": "integer"},
            "line_count": {"type": "integer"},
        },
    }
    timeout_seconds = 5
    rate_limit_per_minute = 300

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        text = input_data["resume_text"]
        normalized = "\n".join(line.strip() for line in text.splitlines() if line.strip())
        return {
            "normalized_text": normalized,
            "word_count": len(normalized.split()),
            "char_count": len(normalized),
            "line_count": len(normalized.splitlines()),
        }

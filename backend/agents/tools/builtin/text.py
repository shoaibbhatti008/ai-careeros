"""Text utility tools — safe, deterministic, no external access."""

from typing import Any, ClassVar

from agents.tools.base import BaseTool, RiskLevel


class TextLengthTool(BaseTool):
    """Return the length of a piece of text."""

    name = "text_length"
    description = "Returns the character and word count of a string."
    risk_level: ClassVar[RiskLevel] = RiskLevel.LOW
    allowed_agents: ClassVar[frozenset[str]] = frozenset()
    input_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {"text": {"type": "string"}},
        "required": ["text"],
    }
    output_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "char_count": {"type": "integer"},
            "word_count": {"type": "integer"},
        },
    }
    timeout_seconds = 5
    rate_limit_per_minute = 1000

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        text = input_data["text"]
        return {
            "char_count": len(text),
            "word_count": len(text.split()),
        }


class TextNormalizeTool(BaseTool):
    """Normalize whitespace and casing of a string."""

    name = "text_normalize"
    description = "Normalizes whitespace and optionally lowercases a string."
    risk_level: ClassVar[RiskLevel] = RiskLevel.LOW
    allowed_agents: ClassVar[frozenset[str]] = frozenset()
    input_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "text": {"type": "string"},
            "lowercase": {"type": "boolean"},
        },
        "required": ["text"],
    }
    output_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {"text": {"type": "string"}},
    }
    timeout_seconds = 5
    rate_limit_per_minute = 1000

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        text = " ".join(input_data["text"].split())
        if input_data.get("lowercase", False):
            text = text.lower()
        return {"text": text}

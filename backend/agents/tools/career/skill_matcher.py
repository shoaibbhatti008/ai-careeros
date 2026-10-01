"""
SkillMatcherTool: compares two skill sets and returns a match analysis.

Risk: LOW. Set operations only.
"""

from typing import Any, ClassVar

from agents.tools.base import BaseTool, RiskLevel


class SkillMatcherTool(BaseTool):
    """
    Compare candidate skills vs required skills.

    Returns:
        matched:      skills present in both
        missing:      required skills not present in candidate
        extra:        candidate skills not in required
        match_score:  0.0–1.0 (ratio of matched to required)
    """

    name = "skill_matcher"
    description = "Compares two skill sets and returns a match score."
    risk_level: ClassVar[RiskLevel] = RiskLevel.LOW
    allowed_agents: ClassVar[frozenset[str]] = frozenset({"job_agent"})
    input_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "candidate_skills": {"type": "array", "items": {"type": "string"}},
            "required_skills": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["candidate_skills", "required_skills"],
    }
    output_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "matched": {"type": "array"},
            "missing": {"type": "array"},
            "extra": {"type": "array"},
            "match_score": {"type": "number"},
        },
    }
    timeout_seconds = 5
    rate_limit_per_minute = 300

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        candidate = {s.lower().strip() for s in input_data["candidate_skills"] if s}
        required = {s.lower().strip() for s in input_data["required_skills"] if s}

        matched = sorted(candidate & required)
        missing = sorted(required - candidate)
        extra = sorted(candidate - required)

        if not required:
            score = 1.0 if candidate else 0.0
        else:
            score = round(len(matched) / len(required), 4)

        return {
            "matched": matched,
            "missing": missing,
            "extra": extra,
            "match_score": score,
        }

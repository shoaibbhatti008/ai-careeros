"""
SkillGapAgent: identifies skill gaps for a target role.

The agent:
1. Analyzes the gap between current skills and required skills
2. Prioritizes gaps (critical → high → medium → low)
3. Returns a structured report with counts and match score

The agent uses only LOW-risk tools. No LLM required.
"""

from typing import Any

from agents.base import BaseAgent
from agents.registry import register_agent
from agents.result import AgentResult


@register_agent
class SkillGapAgent(BaseAgent):
    """Analyzes skill gaps for a target role."""

    name = "skill_gap_agent"
    description = "Identifies and prioritizes missing skills for a target role."
    allowed_tools = frozenset({"skill_gap_analyzer", "skill_extractor"})

    input_schema = {
        "type": "object",
        "properties": {
            "current_skills": {"type": "array", "items": {"type": "string"}},
            "required_skills": {"type": "array", "items": {"type": "string"}},
            "target_role": {"type": "string"},
        },
        "required": ["current_skills", "required_skills"],
    }

    output_schema = {
        "type": "object",
        "properties": {
            "target_role": {"type": "string"},
            "missing_skills": {"type": "array"},
            "matched_skills": {"type": "array"},
            "priority_counts": {"type": "object"},
            "match_score": {"type": "number"},
        },
    }

    def run(self, input_data: dict[str, Any]) -> AgentResult:
        current_skills = input_data.get("current_skills", []) or []
        required_skills = input_data.get("required_skills", []) or []
        target_role = (input_data.get("target_role") or "").strip()

        if not required_skills:
            return AgentResult.failed("required_skills is required and cannot be empty.")

        # Analyze gap
        analysis = self.call_tool(
            "skill_gap_analyzer",
            current_skills=current_skills,
            required_skills=required_skills,
            target_role=target_role,
        )

        missing = analysis.get("missing_skills", [])
        matched = analysis.get("matched_skills", [])
        counts = analysis.get("priority_counts", {})
        score = analysis.get("match_score", 0.0)

        output = {
            "target_role": target_role or None,
            "missing_skills": missing,
            "matched_skills": matched,
            "priority_counts": counts,
            "match_score": score,
        }

        summary = (
            f"Gap analysis for '{target_role or 'unspecified role'}': "
            f"match {score:.0%}, "
            f"{counts.get('critical', 0)} critical / "
            f"{counts.get('high', 0)} high priority gaps."
        )

        return AgentResult.completed(
            output=output,
            summary=summary,
            usage={
                "steps": self.context.usage.steps,
                "tool_calls": self.context.usage.tool_calls,
            },
        )

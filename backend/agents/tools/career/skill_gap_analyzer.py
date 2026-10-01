"""
SkillGapAnalyzerTool: identifies missing skills for a target role.

Risk: LOW. Set operations + priority heuristics. No external access.

The tool compares a candidate's skills against a curated set of
"required skills" for a target role and produces a prioritized gap list.
"""

from typing import Any, ClassVar

from agents.tools.base import BaseTool, RiskLevel

# Priority keywords per skill (used to rank gap importance)
HIGH_PRIORITY_SKILLS: frozenset[str] = frozenset(
    {
        # Core programming languages
        "python",
        "javascript",
        "typescript",
        "java",
        "go",
        # Core frameworks for target roles
        "django",
        "react",
        "fastapi",
        # Critical infra
        "docker",
        "kubernetes",
        "aws",
        # Data
        "postgresql",
        "redis",
        "sql",
    }
)

MEDIUM_PRIORITY_SKILLS: frozenset[str] = frozenset(
    {
        "graphql",
        "rest",
        "grpc",
        "terraform",
        "github actions",
        "ci/cd",
        "mongodb",
        "elasticsearch",
        "pandas",
        "numpy",
    }
)


class SkillGapAnalyzerTool(BaseTool):
    """
    Analyze skill gaps for a target role.

    Input:
        current_skills:  list[str]
        required_skills: list[str]
        target_role:     str (optional)

    Output:
        missing_skills: list of {skill, priority, importance}
        matched_skills: list[str]
        priority_counts: {critical: N, high: N, medium: N, low: N}
        match_score:    float (0.0–1.0)
    """

    name = "skill_gap_analyzer"
    description = "Identifies missing skills and assigns priority per gap."
    risk_level: ClassVar[RiskLevel] = RiskLevel.LOW
    allowed_agents: ClassVar[frozenset[str]] = frozenset({"skill_gap_agent"})
    input_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "current_skills": {"type": "array", "items": {"type": "string"}},
            "required_skills": {"type": "array", "items": {"type": "string"}},
            "target_role": {"type": "string"},
        },
        "required": ["current_skills", "required_skills"],
    }
    output_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "missing_skills": {"type": "array"},
            "matched_skills": {"type": "array"},
            "priority_counts": {"type": "object"},
            "match_score": {"type": "number"},
        },
    }
    timeout_seconds = 5
    rate_limit_per_minute = 300

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        current = {s.lower().strip() for s in input_data["current_skills"] if s}
        required = {s.lower().strip() for s in input_data["required_skills"] if s}

        matched = sorted(current & required)
        missing = sorted(required - current)

        # Assign priority per gap
        missing_with_priority: list[dict[str, Any]] = []
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for skill in missing:
            priority = self._classify_priority(skill)
            importance = self._importance_score(priority)
            missing_with_priority.append(
                {
                    "skill": skill,
                    "priority": priority,
                    "importance": importance,
                }
            )
            counts[priority] += 1

        # Sort: critical first, then high, etc.
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        missing_with_priority.sort(key=lambda x: (priority_order[x["priority"]], -x["importance"]))

        if not required:
            match_score = 1.0 if current else 0.0
        else:
            match_score = round(len(matched) / len(required), 4)

        return {
            "missing_skills": missing_with_priority,
            "matched_skills": matched,
            "priority_counts": counts,
            "match_score": match_score,
        }

    @staticmethod
    def _classify_priority(skill: str) -> str:
        """Classify a skill's priority based on curated sets."""
        if skill in HIGH_PRIORITY_SKILLS:
            return "critical"
        if skill in MEDIUM_PRIORITY_SKILLS:
            return "high"
        # Anything else that was explicitly required → medium
        return "medium"

    @staticmethod
    def _importance_score(priority: str) -> float:
        """Map priority to a numeric importance (0.0–1.0)."""
        return {
            "critical": 1.0,
            "high": 0.75,
            "medium": 0.5,
            "low": 0.25,
        }[priority]

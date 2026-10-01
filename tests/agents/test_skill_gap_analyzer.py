"""Tests for SkillGapAnalyzerTool."""

from agents.tools.base import ToolContext
from agents.tools.career.skill_gap_analyzer import SkillGapAnalyzerTool


def _run(
    current: list[str],
    required: list[str],
    target_role: str = "",
) -> dict:
    tool = SkillGapAnalyzerTool(ToolContext(user_id="u1"))
    result = tool.execute(
        {
            "current_skills": current,
            "required_skills": required,
            "target_role": target_role,
        }
    )
    assert result.success is True
    return result.data


class TestSkillGapAnalyzer:
    def test_no_gap_when_all_matched(self):
        result = _run(["python", "django"], ["python", "django"])
        assert result["missing_skills"] == []
        assert result["match_score"] == 1.0

    def test_identifies_missing_skills(self):
        result = _run(["python"], ["python", "django", "kubernetes"])
        missing_names = [g["skill"] for g in result["missing_skills"]]
        assert "django" in missing_names
        assert "kubernetes" in missing_names

    def test_prioritizes_critical_skills(self):
        result = _run(["python"], ["python", "django", "some_rare_skill"])
        gaps = result["missing_skills"]
        # django is critical (in HIGH_PRIORITY_SKILLS); some_rare_skill is medium
        django_gap = next(g for g in gaps if g["skill"] == "django")
        assert django_gap["priority"] == "critical"

    def test_prioritizes_high_skills(self):
        result = _run([], ["terraform"])
        gaps = result["missing_skills"]
        assert gaps[0]["priority"] == "high"

    def test_unknown_skills_get_medium_priority(self):
        result = _run([], ["some_random_skill_xyz"])
        gaps = result["missing_skills"]
        assert gaps[0]["priority"] == "medium"

    def test_critical_skills_sorted_first(self):
        result = _run(
            [],
            ["some_random_skill", "django", "terraform"],
        )
        priorities = [g["priority"] for g in result["missing_skills"]]
        # critical (django) → high (terraform) → medium (random)
        assert priorities[0] == "critical"
        assert priorities[-1] == "medium"

    def test_importance_score_matches_priority(self):
        result = _run([], ["django"])
        gap = result["missing_skills"][0]
        assert gap["priority"] == "critical"
        assert gap["importance"] == 1.0

    def test_priority_counts(self):
        result = _run([], ["python", "django", "terraform", "some_random_skill"])
        counts = result["priority_counts"]
        # python, django → critical (2)
        # terraform → high (1)
        # some_random_skill → medium (1)
        assert counts["critical"] == 2
        assert counts["high"] == 1
        assert counts["medium"] == 1

    def test_match_score_partial(self):
        result = _run(["python"], ["python", "django"])
        assert result["match_score"] == 0.5

    def test_match_score_zero(self):
        result = _run([], ["python", "django"])
        assert result["match_score"] == 0.0

    def test_case_insensitive(self):
        result = _run(["Python", "Django"], ["python", "django"])
        assert result["match_score"] == 1.0
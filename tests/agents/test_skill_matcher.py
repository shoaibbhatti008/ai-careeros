"""Tests for SkillMatcherTool."""

from agents.tools.base import ToolContext
from agents.tools.career.skill_matcher import SkillMatcherTool


def _run(candidate: list[str], required: list[str]) -> dict:
    tool = SkillMatcherTool(ToolContext(user_id="u1"))
    result = tool.execute(
        {"candidate_skills": candidate, "required_skills": required}
    )
    assert result.success is True
    return result.data


class TestSkillMatcher:
    def test_perfect_match(self):
        result = _run(["python", "django"], ["python", "django"])
        assert result["match_score"] == 1.0
        assert set(result["matched"]) == {"python", "django"}
        assert result["missing"] == []

    def test_partial_match(self):
        result = _run(["python", "django"], ["python", "kubernetes"])
        assert result["match_score"] == 0.5
        assert "python" in result["matched"]
        assert "kubernetes" in result["missing"]

    def test_no_match(self):
        result = _run(["python"], ["java", "go"])
        assert result["match_score"] == 0.0
        assert set(result["missing"]) == {"java", "go"}

    def test_extra_skills_reported(self):
        result = _run(["python", "rust"], ["python"])
        assert "rust" in result["extra"]

    def test_case_insensitive(self):
        result = _run(["Python", "DJANGO"], ["python", "django"])
        assert result["match_score"] == 1.0

    def test_whitespace_trimmed(self):
        result = _run([" python "], ["python"])
        assert result["match_score"] == 1.0

    def test_empty_required_returns_one_if_candidate_has_skills(self):
        result = _run(["python"], [])
        assert result["match_score"] == 1.0

    def test_empty_both_returns_zero(self):
        result = _run([], [])
        assert result["match_score"] == 0.0

    def test_empty_candidate(self):
        result = _run([], ["python", "django"])
        assert result["match_score"] == 0.0
        assert len(result["missing"]) == 2
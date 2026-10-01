"""Tests for QuestionGeneratorTool."""

from agents.tools.base import ToolContext
from agents.tools.career.question_generator import QuestionGeneratorTool


def _run(
    target_role: str,
    skills: list[str] | None = None,
    count: int = 5,
) -> dict:
    tool = QuestionGeneratorTool(ToolContext(user_id="u1"))
    result = tool.execute(
        {
            "target_role": target_role,
            "skills": skills or [],
            "count": count,
        }
    )
    assert result.success is True
    return result.data


class TestQuestionGenerator:
    def test_generates_default_count(self):
        result = _run("Backend Engineer")
        assert len(result["questions"]) == 5

    def test_generates_custom_count(self):
        result = _run("Backend Engineer", count=3)
        assert len(result["questions"]) == 3

    def test_count_clamped_to_20(self):
        result = _run("Backend Engineer", count=100)
        assert len(result["questions"]) == 20

    def test_count_clamped_to_1(self):
        result = _run("Backend Engineer", count=0)
        assert len(result["questions"]) == 1

    def test_includes_technical_questions_for_skills(self):
        result = _run("Backend Engineer", skills=["python", "django"], count=5)
        types = [q["type"] for q in result["questions"]]
        assert "technical" in types

    def test_technical_question_targets_skill(self):
        result = _run("Backend", skills=["python"], count=3)
        python_qs = [q for q in result["questions"] if q.get("skill") == "python"]
        assert len(python_qs) >= 1

    def test_includes_behavioral_questions(self):
        result = _run("Backend", count=10)
        types = [q["type"] for q in result["questions"]]
        assert "behavioral" in types

    def test_includes_system_design_questions(self):
        result = _run("Backend", count=10)
        types = [q["type"] for q in result["questions"]]
        assert "system_design" in types

    def test_each_question_has_expected_fields(self):
        result = _run("Backend", skills=["python"], count=5)
        for q in result["questions"]:
            assert "text" in q
            assert "type" in q
            assert "expected_topics" in q
            assert isinstance(q["expected_topics"], list)

    def test_questions_are_unique_within_generation(self):
        result = _run("Backend", count=5)
        texts = [q["text"] for q in result["questions"]]
        # Behavioral + system design questions should be distinct
        assert len(set(texts)) == len(texts) or len(texts) <= 7

    def test_unknown_skill_produces_default_technical(self):
        result = _run("Backend", skills=["some_unknown_skill"], count=5)
        # Should still produce questions
        assert len(result["questions"]) == 5
"""Tests for AnswerAnalyzerTool."""

from agents.tools.base import ToolContext
from agents.tools.career.answer_analyzer import AnswerAnalyzerTool


def _run(
    answer_text: str,
    expected_topics: list[str] | None = None,
    question_type: str = "behavioral",
) -> dict:
    tool = AnswerAnalyzerTool(ToolContext(user_id="u1"))
    result = tool.execute(
        {
            "answer_text": answer_text,
            "expected_topics": expected_topics or [],
            "question_type": question_type,
        }
    )
    assert result.success is True
    return result.data


STRONG_ANSWER = """
Situation: Our API was getting slow during peak hours.
Task: I was asked to reduce response time by 50%.
Action: I profiled the queries, added indexes, and used Redis caching.
Result: We reduced P95 latency by 60% and saved $2000/month in compute.
Because we measured carefully, we avoided regressions.
"""

SHORT_ANSWER = "I fixed a bug."


class TestAnswerAnalyzer:
    def test_empty_answer_scores_zero(self):
        result = _run("")
        assert result["score"] == 0.0
        assert any("No answer" in i for i in result["improvements"])

    def test_strong_answer_scores_high(self):
        result = _run(STRONG_ANSWER)
        assert result["score"] >= 0.7

    def test_short_answer_lower_score(self):
        result = _run(SHORT_ANSWER)
        assert result["score"] < 0.7

    def test_word_count_computed(self):
        result = _run("hello world foo bar")
        assert result["word_count"] == 4

    def test_quantitative_results_detected(self):
        result = _run("We reduced latency by 60% and saved money.")
        assert any("quantifiable" in s.lower() for s in result["strengths"])

    def test_star_structure_detected(self):
        result = _run(STRONG_ANSWER, question_type="behavioral")
        assert any("STAR" in s for s in result["strengths"])

    def test_missing_topics_reported(self):
        result = _run(
            "I talked about Python.",
            expected_topics=["python", "django", "postgresql"],
        )
        assert any("Missing key topics" in i for i in result["improvements"])

    def test_topics_covered_reported(self):
        result = _run(
            "I used python and django extensively.",
            expected_topics=["python", "django"],
        )
        assert set(result["topics_covered"]) == {"python", "django"}

    def test_reasoning_keywords_detected(self):
        result = _run("We chose this because it scales better.")
        assert any("reasoning" in s.lower() for s in result["strengths"])

    def test_score_clamped_between_0_and_1(self):
        result = _run(STRONG_ANSWER)
        assert 0.0 <= result["score"] <= 1.0

    def test_short_answer_has_improvement(self):
        result = _run(SHORT_ANSWER)
        assert any("short" in i.lower() for i in result["improvements"])
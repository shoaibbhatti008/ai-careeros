"""
AnswerAnalyzerTool: analyzes an interview answer and provides feedback.

Risk: LOW. Deterministic heuristics. No external access, no LLM.

Note: This is a heuristic analyzer. A future LLM-backed tool can
provide deeper feedback.
"""

from typing import Any, ClassVar

from agents.tools.base import BaseTool, RiskLevel


class AnswerAnalyzerTool(BaseTool):
    """
    Analyze a single interview answer.

    Input:
        answer_text:       str
        expected_topics:   list[str]  (optional)
        question_type:     "behavioral" | "technical" | "system_design"

    Output:
        score:           float (0.0–1.0)
        strengths:       list[str]
        improvements:    list[str]
        word_count:      int
        topics_covered:  list[str]
    """

    name = "answer_analyzer"
    description = "Analyzes an interview answer and returns structured feedback."
    risk_level: ClassVar[RiskLevel] = RiskLevel.LOW
    allowed_agents: ClassVar[frozenset[str]] = frozenset({"interview_agent"})
    input_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "answer_text": {"type": "string"},
            "expected_topics": {"type": "array", "items": {"type": "string"}},
            "question_type": {"type": "string"},
        },
        "required": ["answer_text"],
    }
    output_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "score": {"type": "number"},
            "strengths": {"type": "array"},
            "improvements": {"type": "array"},
            "word_count": {"type": "integer"},
            "topics_covered": {"type": "array"},
        },
    }
    timeout_seconds = 5
    rate_limit_per_minute = 300

    # Structural indicators of a strong answer
    STAR_INDICATORS = ("situation", "task", "action", "result")
    QUANT_INDICATORS = ("%", "percent", "reduced", "increased", "saved", "improved")

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        text = input_data.get("answer_text", "").strip()
        expected_topics = [t.lower().strip() for t in input_data.get("expected_topics", []) if t]
        question_type = input_data.get("question_type", "")

        if not text:
            return {
                "score": 0.0,
                "strengths": [],
                "improvements": ["No answer was provided."],
                "word_count": 0,
                "topics_covered": [],
            }

        lower = text.lower()
        words = text.split()
        word_count = len(words)

        strengths: list[str] = []
        improvements: list[str] = []
        score = 0.5  # baseline

        # Length check
        if word_count >= 80:
            strengths.append("Answer is detailed and specific.")
            score += 0.1
        elif word_count < 30:
            improvements.append("Answer is very short; add more detail.")
            score -= 0.15

        # STAR indicators (for behavioral)
        if question_type == "behavioral":
            star_hits = sum(1 for kw in self.STAR_INDICATORS if kw in lower)
            if star_hits >= 3:
                strengths.append("Uses STAR structure (situation, task, action, result).")
                score += 0.15
            elif star_hits >= 1:
                improvements.append("Consider using STAR structure for clarity.")

        # Quantitative results
        if any(kw in lower for kw in self.QUANT_INDICATORS):
            strengths.append("Includes quantifiable results.")
            score += 0.1
        else:
            improvements.append("Add measurable outcomes (percentages, numbers).")

        # Topic coverage
        topics_covered = [t for t in expected_topics if t in lower]
        if expected_topics:
            coverage = len(topics_covered) / len(expected_topics)
            if coverage >= 0.8:
                strengths.append("Covers nearly all expected topics.")
                score += 0.15
            elif coverage < 0.5:
                improvements.append(
                    f"Missing key topics: "
                    f"{', '.join(t for t in expected_topics if t not in topics_covered)}"
                )

        # Structural quality: has "because", "so", "therefore" → reasoning
        if any(kw in lower for kw in ("because", "so that", "therefore", "resulted in")):
            strengths.append("Explains reasoning and outcomes.")
            score += 0.05

        # Filler words penalty
        filler_count = sum(lower.count(w) for w in (" um ", " uh ", " like ", " you know "))
        if filler_count > 5:
            improvements.append("Reduce filler words (um, uh, like, you know).")
            score -= 0.05

        # Clamp
        score = round(max(0.0, min(1.0, score)), 2)

        return {
            "score": score,
            "strengths": strengths,
            "improvements": improvements,
            "word_count": word_count,
            "topics_covered": topics_covered,
        }

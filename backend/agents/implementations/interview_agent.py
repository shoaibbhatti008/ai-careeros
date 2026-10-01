"""
InterviewAgent: conducts a mock interview.

Given a target role and optional skills, the agent:
1. Generates a set of interview questions
2. Optionally analyzes answers (if provided)
3. Returns a structured interview report

The agent is a mock interviewer. It does NOT run real interviews and
does NOT store any data. All processing is stateless.
"""

from typing import Any

from agents.base import BaseAgent
from agents.registry import register_agent
from agents.result import AgentResult


@register_agent
class InterviewAgent(BaseAgent):
    """Conducts a mock interview session."""

    name = "interview_agent"
    description = "Generates interview questions and analyzes answers."
    allowed_tools = frozenset({"question_generator", "answer_analyzer"})

    input_schema = {
        "type": "object",
        "properties": {
            "target_role": {"type": "string"},
            "skills": {"type": "array", "items": {"type": "string"}},
            "count": {"type": "integer"},
            "answers": {"type": "array", "items": {"type": "object"}},
        },
        "required": ["target_role"],
    }

    output_schema = {
        "type": "object",
        "properties": {
            "target_role": {"type": "string"},
            "questions": {"type": "array"},
            "answer_feedback": {"type": "array"},
            "overall_score": {"type": ["number", "null"]},
        },
    }

    def run(self, input_data: dict[str, Any]) -> AgentResult:
        target_role = (input_data.get("target_role") or "").strip()
        if not target_role:
            return AgentResult.failed("target_role is required.")

        skills = input_data.get("skills", []) or []
        count = int(input_data.get("count", 5))
        answers = input_data.get("answers", []) or []

        # 1. Generate questions
        generated = self.call_tool(
            "question_generator",
            target_role=target_role,
            skills=skills,
            count=count,
        )
        questions = generated.get("questions", [])

        # 2. If answers provided, analyze each (pairing by index)
        answer_feedback: list[dict[str, Any]] = []
        for i, answer in enumerate(answers):
            if i >= len(questions):
                break
            question = questions[i]
            answer_text = answer.get("answer_text", "")
            if not answer_text:
                continue

            feedback = self.call_tool(
                "answer_analyzer",
                answer_text=answer_text,
                expected_topics=question.get("expected_topics", []),
                question_type=question.get("type", ""),
            )
            answer_feedback.append(
                {
                    "question_index": i,
                    "question_text": question["text"],
                    "score": feedback["score"],
                    "strengths": feedback["strengths"],
                    "improvements": feedback["improvements"],
                    "word_count": feedback["word_count"],
                }
            )

        # 3. Overall score = average of feedback scores, or None
        overall_score = (
            round(sum(f["score"] for f in answer_feedback) / len(answer_feedback), 2)
            if answer_feedback
            else None
        )

        output = {
            "target_role": target_role,
            "questions": questions,
            "answer_feedback": answer_feedback,
            "overall_score": overall_score,
        }

        summary = f"Generated {len(questions)} questions for '{target_role}'."
        if answer_feedback:
            summary += f" Analyzed {len(answer_feedback)} answers (avg {overall_score:.0%})."

        return AgentResult.completed(
            output=output,
            summary=summary,
            usage={
                "steps": self.context.usage.steps,
                "tool_calls": self.context.usage.tool_calls,
            },
        )

"""Tests for InterviewAgent."""

from uuid import uuid4

import pytest

from agents.context import AgentBudgets, AgentContext
from agents.implementations.interview_agent import InterviewAgent
from agents.registry import AgentRegistry
from agents.tools.base import ToolContext
from agents.tools.career.answer_analyzer import AnswerAnalyzerTool
from agents.tools.career.question_generator import QuestionGeneratorTool
from agents.tools.registry import ToolRegistry, execute_tool


@pytest.fixture(autouse=True)
def register_interview_agent_and_tools():
    ToolRegistry._tools.setdefault("question_generator", QuestionGeneratorTool)
    ToolRegistry._tools.setdefault("answer_analyzer", AnswerAnalyzerTool)
    AgentRegistry._agents.setdefault("interview_agent", InterviewAgent)
    yield


def _make_context(*, allowed_tools: frozenset[str] | None = None) -> AgentContext:
    tools = allowed_tools or frozenset({"question_generator", "answer_analyzer"})

    def tool_executor(tool_name: str, **kwargs: object) -> dict:
        tool_context = ToolContext(user_id=str(uuid4()))
        return execute_tool(
            tool_name=tool_name,
            agent_name="interview_agent",
            agent_allowed_tools=InterviewAgent.allowed_tools,
            context_allowed_tools=tools,
            input_data=dict(kwargs),
            tool_context=tool_context,
        )

    return AgentContext(
        user_id=uuid4(),
        allowed_tools=tools,
        tool_executor=tool_executor,
    )


class TestInterviewAgent:
    def test_generates_questions(self):
        agent = InterviewAgent(_make_context())
        result = agent.execute({"target_role": "Backend Engineer", "count": 5})
        assert result.status.value == "completed"
        assert len(result.output["questions"]) == 5

    def test_questions_include_skills(self):
        agent = InterviewAgent(_make_context())
        result = agent.execute(
            {
                "target_role": "Backend Engineer",
                "skills": ["python", "django"],
                "count": 5,
            }
        )
        skills_in_questions = [
            q.get("skill") for q in result.output["questions"] if q.get("skill")
        ]
        assert "python" in skills_in_skills_or_empty(skills_in_questions) or len(
            skills_in_questions
        ) >= 1

    def test_analyzes_answers(self):
        agent = InterviewAgent(_make_context())
        result = agent.execute(
            {
                "target_role": "Backend",
                "count": 2,
                "answers": [
                    {
                        "answer_text": "Situation: We had a problem. Action: I fixed it. "
                        "Result: 60% improvement."
                    },
                    {"answer_text": "Short answer."},
                ],
            }
        )
        assert result.status.value == "completed"
        assert len(result.output["answer_feedback"]) == 2

    def test_overall_score_computed(self):
        agent = InterviewAgent(_make_context())
        result = agent.execute(
            {
                "target_role": "Backend",
                "count": 2,
                "answers": [
                    {"answer_text": "Good detailed answer with 80+ words. " * 5},
                    {"answer_text": "Good detailed answer with 80+ words. " * 5},
                ],
            }
        )
        assert result.output["overall_score"] is not None
        assert 0.0 <= result.output["overall_score"] <= 1.0

    def test_overall_score_none_without_answers(self):
        agent = InterviewAgent(_make_context())
        result = agent.execute({"target_role": "Backend", "count": 3})
        assert result.output["overall_score"] is None

    def test_empty_target_role_fails(self):
        agent = InterviewAgent(_make_context())
        result = agent.execute({"target_role": ""})
        assert result.status.value == "failed"

    def test_agent_is_registered(self):
        assert AgentRegistry.get("interview_agent") is InterviewAgent

    def test_agent_declares_two_tools(self):
        assert InterviewAgent.allowed_tools == frozenset(
            {"question_generator", "answer_analyzer"}
        )

    def test_respects_allowlist(self):
        ctx = _make_context(allowed_tools=frozenset({"question_generator"}))
        agent = InterviewAgent(ctx)
        result = agent.execute(
            {
                "target_role": "Backend",
                "count": 2,
                "answers": [{"answer_text": "Answer"}],
            }
        )
        assert result.status.value == "failed"

    def test_respects_budget(self):
        ctx = _make_context()
        ctx.budgets = AgentBudgets(max_tool_calls=0)
        agent = InterviewAgent(ctx)
        result = agent.execute({"target_role": "Backend", "count": 3})
        assert result.status.value == "failed"

    def test_summary_present(self):
        agent = InterviewAgent(_make_context())
        result = agent.execute({"target_role": "Backend", "count": 3})
        assert result.summary
        assert "Backend" in result.summary

    def test_summary_includes_answer_count(self):
        agent = InterviewAgent(_make_context())
        result = agent.execute(
            {
                "target_role": "Backend",
                "count": 2,
                "answers": [{"answer_text": "Hello world. " * 20}],
            }
        )
        assert "1" in result.summary  # 1 answer analyzed

    def test_output_shape(self):
        agent = InterviewAgent(_make_context())
        result = agent.execute({"target_role": "Backend", "count": 3})
        assert isinstance(result.output["questions"], list)
        assert isinstance(result.output["answer_feedback"], list)
        assert result.output["overall_score"] is None

    def test_skips_empty_answers(self):
        agent = InterviewAgent(_make_context())
        result = agent.execute(
            {
                "target_role": "Backend",
                "count": 3,
                "answers": [{"answer_text": ""}, {"answer_text": "Good answer. " * 20}],
            }
        )
        # Only one answer analyzed
        assert len(result.output["answer_feedback"]) == 1


# Helper for one of the tests
def skills_in_skills_or_empty(skills):
    return skills if skills else []
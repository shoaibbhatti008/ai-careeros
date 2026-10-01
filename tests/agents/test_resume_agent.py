"""Tests for ResumeAgent."""

from uuid import uuid4

import pytest

from agents.context import AgentBudgets, AgentContext
from agents.implementations.resume_agent import ResumeAgent
from agents.registry import AgentRegistry
from agents.tools.base import ToolContext
from agents.tools.career import ResumeReaderTool, SkillExtractorTool
from agents.tools.registry import ToolRegistry, execute_tool


# ==========================================================
# Fixtures
# ==========================================================


@pytest.fixture(autouse=True)
def register_tools_and_agent():
    """Register career tools + resume agent for tests."""
    ToolRegistry._tools.setdefault("resume_reader", ResumeReaderTool)
    ToolRegistry._tools.setdefault("skill_extractor", SkillExtractorTool)
    AgentRegistry._agents.setdefault("resume_agent", ResumeAgent)
    yield


def _make_context(*, allowed_tools: frozenset[str] | None = None) -> AgentContext:
    """Create an AgentContext wired to a real tool executor."""
    tools = allowed_tools or frozenset({"resume_reader", "skill_extractor"})

    def tool_executor(tool_name: str, **kwargs: object) -> dict:
        tool_context = ToolContext(user_id=str(uuid4()))
        tool_cls = ToolRegistry.get(tool_name)
        return execute_tool(
            tool_name=tool_name,
            agent_name="resume_agent",
            agent_allowed_tools=ResumeAgent.allowed_tools,
            context_allowed_tools=tools,
            input_data=dict(kwargs),
            tool_context=tool_context,
        )

    return AgentContext(
        user_id=uuid4(),
        allowed_tools=tools,
        tool_executor=tool_executor,
    )


SAMPLE_RESUME = """
John Doe
Senior Software Engineer

Experience
- 5 years building backend services with Python and Django
- Designed REST APIs using PostgreSQL and Redis
- Deployed microservices with Docker and Kubernetes on AWS
- Built CI/CD pipelines with GitHub Actions

Education
BS Computer Science, 2018

Skills
Python, Django, PostgreSQL, Redis, Docker, Kubernetes, AWS, Git, Linux, REST
"""


# ==========================================================
# Tests
# ==========================================================


class TestResumeAgent:
    def test_analyzes_complete_resume(self):
        agent = ResumeAgent(_make_context())
        result = agent.execute({"resume_text": SAMPLE_RESUME})
        assert result.status.value == "completed"
        assert "skills" in result.output
        assert result.output["word_count"] > 0

    def test_extracts_known_skills(self):
        agent = ResumeAgent(_make_context())
        result = agent.execute({"resume_text": SAMPLE_RESUME})
        skills = result.output["skills"]
        assert "python" in skills
        assert "django" in skills
        assert "docker" in skills
        assert "kubernetes" in skills

    def test_detects_missing_sections(self):
        agent = ResumeAgent(_make_context())
        result = agent.execute({"resume_text": "Just some plain text."})
        hints = result.output["ats_hints"]
        assert any("Experience" in h for h in hints)
        assert any("Education" in h for h in hints)
        assert any("Skills" in h for h in hints)

    def test_no_ats_hints_for_complete_resume(self):
        agent = ResumeAgent(_make_context())
        result = agent.execute({"resume_text": SAMPLE_RESUME})
        assert result.output["ats_hints"] == []

    def test_target_role_is_reported(self):
        agent = ResumeAgent(_make_context())
        result = agent.execute(
            {"resume_text": SAMPLE_RESUME, "target_role": "Backend Engineer"}
        )
        assert result.output["target_role"] == "Backend Engineer"

    def test_missing_target_role_is_none(self):
        agent = ResumeAgent(_make_context())
        result = agent.execute({"resume_text": SAMPLE_RESUME})
        assert result.output["target_role"] is None

    def test_empty_resume_fails(self):
        agent = ResumeAgent(_make_context())
        result = agent.execute({"resume_text": ""})
        assert result.status.value == "failed"

    def test_short_resume_triggers_improvement(self):
        agent = ResumeAgent(_make_context())
        result = agent.execute({"resume_text": "Python dev."})
        improvements = result.output["improvements"]
        assert any("short" in i.lower() for i in improvements)

    def test_long_resume_has_strength(self):
        agent = ResumeAgent(_make_context())
        # Repeat 10x to make it clearly long (>200 words)
        long_text = SAMPLE_RESUME * 10
        result = agent.execute({"resume_text": long_text})
        assert any("substantial" in s.lower() for s in result.output["strengths"])

    def test_agent_respects_tool_allowlist(self):
        # Only allow resume_reader, not skill_extractor
        context = _make_context(allowed_tools=frozenset({"resume_reader"}))
        agent = ResumeAgent(context)
        result = agent.execute({"resume_text": SAMPLE_RESUME})
        assert result.status.value == "failed"

    def test_agent_respects_tool_budget(self):
        context = _make_context()
        context.budgets = AgentBudgets(max_tool_calls=1)
        agent = ResumeAgent(context)
        result = agent.execute({"resume_text": SAMPLE_RESUME})
        # First tool succeeds, second exceeds budget
        assert result.status.value == "failed"

    def test_agent_is_registered(self):
        agent_cls = AgentRegistry.get("resume_agent")
        assert agent_cls is ResumeAgent

    def test_agent_declares_allowed_tools(self):
        assert "resume_reader" in ResumeAgent.allowed_tools
        assert "skill_extractor" in ResumeAgent.allowed_tools

    def test_agent_cannot_use_other_tools(self):
        assert "database_write" not in ResumeAgent.allowed_tools
        assert "send_email" not in ResumeAgent.allowed_tools

    def test_output_has_expected_shape(self):
        agent = ResumeAgent(_make_context())
        result = agent.execute({"resume_text": SAMPLE_RESUME})
        output = result.output
        assert isinstance(output["skills"], list)
        assert isinstance(output["strengths"], list)
        assert isinstance(output["improvements"], list)
        assert isinstance(output["ats_hints"], list)
        assert isinstance(output["word_count"], int)

    def test_summary_is_present(self):
        agent = ResumeAgent(_make_context())
        result = agent.execute({"resume_text": SAMPLE_RESUME})
        assert result.summary
        assert "skills" in result.summary.lower() or "words" in result.summary.lower()
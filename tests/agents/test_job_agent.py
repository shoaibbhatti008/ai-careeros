"""Tests for JobAgent."""

from uuid import uuid4

import pytest

from agents.context import AgentBudgets, AgentContext
from agents.implementations.job_agent import JobAgent
from agents.registry import AgentRegistry
from agents.tools.base import ToolContext
from agents.tools.career.job_parser import JobParserTool
from agents.tools.career.skill_extractor import SkillExtractorTool
from agents.tools.career.skill_matcher import SkillMatcherTool
from agents.tools.registry import ToolRegistry, execute_tool


@pytest.fixture(autouse=True)
def register_job_agent_and_tools():
    """Register JobAgent + its tools for tests."""
    ToolRegistry._tools.setdefault("job_parser", JobParserTool)
    ToolRegistry._tools.setdefault("skill_extractor", SkillExtractorTool)
    ToolRegistry._tools.setdefault("skill_matcher", SkillMatcherTool)
    AgentRegistry._agents.setdefault("job_agent", JobAgent)
    yield


def _make_context(*, allowed_tools: frozenset[str] | None = None) -> AgentContext:
    tools = allowed_tools or frozenset(
        {"job_parser", "skill_extractor", "skill_matcher"}
    )

    def tool_executor(tool_name: str, **kwargs: object) -> dict:
        tool_context = ToolContext(user_id=str(uuid4()))
        return execute_tool(
            tool_name=tool_name,
            agent_name="job_agent",
            agent_allowed_tools=JobAgent.allowed_tools,
            context_allowed_tools=tools,
            input_data=dict(kwargs),
            tool_context=tool_context,
        )

    return AgentContext(
        user_id=uuid4(),
        allowed_tools=tools,
        tool_executor=tool_executor,
    )


SAMPLE_JOB = """
Senior Backend Engineer at Acme Corp in Berlin

We are looking for a Senior Backend Engineer to join our platform team.
This is an on-site role based in our Berlin office.

Requirements:
- 5+ years of experience with Python and Django
- Strong knowledge of PostgreSQL and Redis
- Experience with Docker and Kubernetes
- Familiarity with AWS and CI/CD pipelines
- Excellent communication skills
"""


SAMPLE_CANDIDATE_SKILLS = [
    "python",
    "django",
    "postgresql",
    "docker",
]


class TestJobAgent:
    def test_parses_job_description(self):
        agent = JobAgent(_make_context())
        result = agent.execute(
            {"job_text": SAMPLE_JOB, "candidate_skills": SAMPLE_CANDIDATE_SKILLS}
        )
        assert result.status.value == "completed"
        assert "Backend" in result.output["role_title"]
        assert result.output["seniority"] == "senior"
        assert result.output["remote_policy"] == "onsite"

    def test_extracts_required_skills(self):
        agent = JobAgent(_make_context())
        result = agent.execute(
            {"job_text": SAMPLE_JOB, "candidate_skills": SAMPLE_CANDIDATE_SKILLS}
        )
        required = result.output["required_skills"]
        assert "python" in required
        assert "django" in required
        assert "postgresql" in required
        assert "docker" in required
        assert "kubernetes" in required

    def test_computes_match_score(self):
        agent = JobAgent(_make_context())
        result = agent.execute(
            {"job_text": SAMPLE_JOB, "candidate_skills": SAMPLE_CANDIDATE_SKILLS}
        )
        assert result.output["match_score"] > 0.0
        assert result.output["match_score"] <= 1.0

    def test_reports_missing_skills(self):
        agent = JobAgent(_make_context())
        result = agent.execute(
            {"job_text": SAMPLE_JOB, "candidate_skills": SAMPLE_CANDIDATE_SKILLS}
        )
        missing = result.output["missing_skills"]
        # Candidate lacks kubernetes, aws, redis, ci/cd
        assert "kubernetes" in missing

    def test_reports_matched_skills(self):
        agent = JobAgent(_make_context())
        result = agent.execute(
            {"job_text": SAMPLE_JOB, "candidate_skills": SAMPLE_CANDIDATE_SKILLS}
        )
        matched = result.output["matched_skills"]
        assert "python" in matched
        assert "django" in matched
        assert "docker" in matched

    def test_detects_remote_policy(self):
        remote_job = "Remote Senior Engineer\nFully remote position.\nPython and Django."
        agent = JobAgent(_make_context())
        result = agent.execute({"job_text": remote_job, "candidate_skills": []})
        assert result.output["remote_policy"] == "remote"

    def test_detects_hybrid_policy(self):
        hybrid_job = "Hybrid role in London.\nPython, Django."
        agent = JobAgent(_make_context())
        result = agent.execute({"job_text": hybrid_job, "candidate_skills": []})
        assert result.output["remote_policy"] == "hybrid"

    def test_detects_junior_seniority(self):
        junior_job = "Junior Python Developer\nEntry level position."
        agent = JobAgent(_make_context())
        result = agent.execute({"job_text": junior_job, "candidate_skills": []})
        assert result.output["seniority"] == "junior"

    def test_empty_job_text_fails(self):
        agent = JobAgent(_make_context())
        result = agent.execute({"job_text": ""})
        assert result.status.value == "failed"

    def test_no_candidate_skills_is_ok(self):
        agent = JobAgent(_make_context())
        result = agent.execute({"job_text": SAMPLE_JOB})
        assert result.status.value == "completed"
        assert result.output["match_score"] == 0.0

    def test_agent_is_registered(self):
        assert AgentRegistry.get("job_agent") is JobAgent

    def test_agent_declares_three_tools(self):
        assert JobAgent.allowed_tools == frozenset(
            {"job_parser", "skill_extractor", "skill_matcher"}
        )

    def test_respects_tool_allowlist(self):
        ctx = _make_context(allowed_tools=frozenset({"job_parser"}))
        agent = JobAgent(ctx)
        result = agent.execute({"job_text": SAMPLE_JOB, "candidate_skills": []})
        assert result.status.value == "failed"

    def test_respects_tool_budget(self):
        ctx = _make_context()
        ctx.budgets = AgentBudgets(max_tool_calls=1)
        agent = JobAgent(ctx)
        result = agent.execute({"job_text": SAMPLE_JOB, "candidate_skills": []})
        assert result.status.value == "failed"

    def test_output_shape(self):
        agent = JobAgent(_make_context())
        result = agent.execute(
            {"job_text": SAMPLE_JOB, "candidate_skills": SAMPLE_CANDIDATE_SKILLS}
        )
        assert isinstance(result.output["required_skills"], list)
        assert isinstance(result.output["matched_skills"], list)
        assert isinstance(result.output["missing_skills"], list)
        assert isinstance(result.output["extra_skills"], list)
        assert isinstance(result.output["match_score"], float)

    def test_summary_is_present(self):
        agent = JobAgent(_make_context())
        result = agent.execute(
            {"job_text": SAMPLE_JOB, "candidate_skills": SAMPLE_CANDIDATE_SKILLS}
        )
        assert result.summary
        assert "Match score" in result.summary
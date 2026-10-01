"""Tests for SkillGapAgent."""

from uuid import uuid4

import pytest

from agents.context import AgentBudgets, AgentContext
from agents.implementations.skill_gap_agent import SkillGapAgent
from agents.registry import AgentRegistry
from agents.tools.base import ToolContext
from agents.tools.career.skill_extractor import SkillExtractorTool
from agents.tools.career.skill_gap_analyzer import SkillGapAnalyzerTool
from agents.tools.registry import ToolRegistry, execute_tool


@pytest.fixture(autouse=True)
def register_skill_gap_agent_and_tools():
    ToolRegistry._tools.setdefault("skill_gap_analyzer", SkillGapAnalyzerTool)
    ToolRegistry._tools.setdefault("skill_extractor", SkillExtractorTool)
    AgentRegistry._agents.setdefault("skill_gap_agent", SkillGapAgent)
    yield


def _make_context(*, allowed_tools: frozenset[str] | None = None) -> AgentContext:
    tools = allowed_tools or frozenset({"skill_gap_analyzer", "skill_extractor"})

    def tool_executor(tool_name: str, **kwargs: object) -> dict:
        tool_context = ToolContext(user_id=str(uuid4()))
        return execute_tool(
            tool_name=tool_name,
            agent_name="skill_gap_agent",
            agent_allowed_tools=SkillGapAgent.allowed_tools,
            context_allowed_tools=tools,
            input_data=dict(kwargs),
            tool_context=tool_context,
        )

    return AgentContext(
        user_id=uuid4(),
        allowed_tools=tools,
        tool_executor=tool_executor,
    )


class TestSkillGapAgent:
    def test_returns_structured_output(self):
        agent = SkillGapAgent(_make_context())
        result = agent.execute(
            {
                "current_skills": ["python"],
                "required_skills": ["python", "django"],
                "target_role": "Backend Engineer",
            }
        )
        assert result.status.value == "completed"
        assert result.output["target_role"] == "Backend Engineer"
        assert isinstance(result.output["missing_skills"], list)
        assert isinstance(result.output["matched_skills"], list)

    def test_missing_skills_include_django(self):
        agent = SkillGapAgent(_make_context())
        result = agent.execute(
            {
                "current_skills": ["python"],
                "required_skills": ["python", "django"],
            }
        )
        missing_names = [g["skill"] for g in result.output["missing_skills"]]
        assert "django" in missing_names

    def test_match_score_computed(self):
        agent = SkillGapAgent(_make_context())
        result = agent.execute(
            {
                "current_skills": ["python"],
                "required_skills": ["python", "django", "kubernetes"],
            }
        )
        # 1 of 3 matched
        assert result.output["match_score"] == round(1 / 3, 4)

    def test_priority_counts_present(self):
        agent = SkillGapAgent(_make_context())
        result = agent.execute(
            {
                "current_skills": [],
                "required_skills": ["python", "django", "terraform"],
            }
        )
        counts = result.output["priority_counts"]
        assert counts["critical"] >= 2  # python, django
        assert counts["high"] >= 1      # terraform

    def test_no_gap_when_all_matched(self):
        agent = SkillGapAgent(_make_context())
        result = agent.execute(
            {
                "current_skills": ["python", "django"],
                "required_skills": ["python", "django"],
            }
        )
        assert result.output["missing_skills"] == []
        assert result.output["match_score"] == 1.0

    def test_empty_required_skills_fails(self):
        agent = SkillGapAgent(_make_context())
        result = agent.execute(
            {"current_skills": ["python"], "required_skills": []}
        )
        assert result.status.value == "failed"

    def test_target_role_optional(self):
        agent = SkillGapAgent(_make_context())
        result = agent.execute(
            {
                "current_skills": ["python"],
                "required_skills": ["python", "django"],
            }
        )
        assert result.status.value == "completed"
        assert result.output["target_role"] is None

    def test_agent_is_registered(self):
        assert AgentRegistry.get("skill_gap_agent") is SkillGapAgent

    def test_agent_declares_two_tools(self):
        assert SkillGapAgent.allowed_tools == frozenset(
            {"skill_gap_analyzer", "skill_extractor"}
        )

    def test_respects_allowlist(self):
        ctx = _make_context(allowed_tools=frozenset({"skill_extractor"}))
        agent = SkillGapAgent(ctx)
        result = agent.execute(
            {
                "current_skills": ["python"],
                "required_skills": ["python", "django"],
            }
        )
        assert result.status.value == "failed"

    def test_respects_budget(self):
        ctx = _make_context()
        ctx.budgets = AgentBudgets(max_tool_calls=0)
        agent = SkillGapAgent(ctx)
        result = agent.execute(
            {
                "current_skills": ["python"],
                "required_skills": ["python", "django"],
            }
        )
        assert result.status.value == "failed"

    def test_summary_present(self):
        agent = SkillGapAgent(_make_context())
        result = agent.execute(
            {
                "current_skills": ["python"],
                "required_skills": ["python", "django", "terraform"],
                "target_role": "Backend",
            }
        )
        assert result.summary
        assert "Backend" in result.summary
        assert "%" in result.summary

    def test_output_shape(self):
        agent = SkillGapAgent(_make_context())
        result = agent.execute(
            {
                "current_skills": ["python"],
                "required_skills": ["python", "django"],
            }
        )
        assert isinstance(result.output["missing_skills"], list)
        assert isinstance(result.output["matched_skills"], list)
        assert isinstance(result.output["priority_counts"], dict)
        assert isinstance(result.output["match_score"], float)

    def test_missing_skill_has_priority(self):
        agent = SkillGapAgent(_make_context())
        result = agent.execute(
            {
                "current_skills": [],
                "required_skills": ["django"],
            }
        )
        gap = result.output["missing_skills"][0]
        assert "skill" in gap
        assert "priority" in gap
        assert "importance" in gap
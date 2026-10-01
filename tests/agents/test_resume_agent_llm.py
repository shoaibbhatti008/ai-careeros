"""Tests for ResumeAgentLLM using MockLLMProvider."""

from uuid import uuid4

import pytest

from agents.context import AgentBudgets, AgentContext
from agents.implementations.resume_agent_llm import ResumeAgentLLM
from agents.llm.mock import MockLLMProvider
from agents.registry import AgentRegistry
from agents.tools.base import ToolContext
from agents.tools.career.llm_analyzer import LLMAnalyzerTool
from agents.tools.registry import ToolRegistry, execute_tool


@pytest.fixture(autouse=True)
def register_llm_agent():
    """Register the LLM agent and its tool."""
    ToolRegistry._tools.setdefault("llm_analyzer", LLMAnalyzerTool)
    AgentRegistry._agents.setdefault("resume_agent_llm", ResumeAgentLLM)
    yield


def _make_context(
    *,
    llm_response: str,
    allowed_tools: frozenset[str] | None = None,
) -> AgentContext:
    """Build an AgentContext wired to a MockLLMProvider."""
    tools = allowed_tools or frozenset({"llm_analyzer"})
    provider = MockLLMProvider(default_response=llm_response)

    def tool_executor(tool_name: str, **kwargs: object) -> dict:
        tool_context = ToolContext(
            user_id=str(uuid4()),
            metadata={"llm_provider": provider},
        )
        return execute_tool(
            tool_name=tool_name,
            agent_name="resume_agent_llm",
            agent_allowed_tools=ResumeAgentLLM.allowed_tools,
            context_allowed_tools=tools,
            input_data=dict(kwargs),
            tool_context=tool_context,
        )

    return AgentContext(
        user_id=uuid4(),
        allowed_tools=tools,
        tool_executor=tool_executor,
    )


SAMPLE_LLM_RESPONSE = """{
  "skills": ["python", "django", "postgresql"],
  "strengths": ["strong backend experience"],
  "improvements": ["add more metrics"],
  "ats_hints": [],
  "seniority_estimate": "mid",
  "target_role_fit": "Good fit for backend roles"
}"""


class TestResumeAgentLLM:
    def test_analyzes_resume_with_llm(self):
        agent = ResumeAgentLLM(_make_context(llm_response=SAMPLE_LLM_RESPONSE))
        result = agent.execute({"resume_text": "John Doe, Python dev"})
        assert result.status.value == "completed"
        assert "python" in result.output["skills"]
        assert result.output["seniority_estimate"] == "mid"

    def test_output_shape_matches_schema(self):
        agent = ResumeAgentLLM(_make_context(llm_response=SAMPLE_LLM_RESPONSE))
        result = agent.execute({"resume_text": "text"})
        assert isinstance(result.output["skills"], list)
        assert isinstance(result.output["strengths"], list)
        assert isinstance(result.output["improvements"], list)
        assert isinstance(result.output["ats_hints"], list)

    def test_empty_resume_fails(self):
        agent = ResumeAgentLLM(_make_context(llm_response=SAMPLE_LLM_RESPONSE))
        result = agent.execute({"resume_text": ""})
        assert result.status.value == "failed"

    def test_missing_llm_provider_fails(self):
        """If no provider is injected, tool raises and agent fails cleanly."""
        tools = frozenset({"llm_analyzer"})

        def no_provider_executor(tool_name: str, **kwargs: object) -> dict:
            tool_context = ToolContext(user_id=str(uuid4()))  # no provider
            return execute_tool(
                tool_name=tool_name,
                agent_name="resume_agent_llm",
                agent_allowed_tools=ResumeAgentLLM.allowed_tools,
                context_allowed_tools=tools,
                input_data=dict(kwargs),
                tool_context=tool_context,
            )

        ctx = AgentContext(
            user_id=uuid4(),
            allowed_tools=tools,
            tool_executor=no_provider_executor,
        )
        agent = ResumeAgentLLM(ctx)
        result = agent.execute({"resume_text": "text"})
        assert result.status.value == "failed"

    def test_malformed_llm_json_fails(self):
        agent = ResumeAgentLLM(_make_context(llm_response="not json at all"))
        result = agent.execute({"resume_text": "text"})
        assert result.status.value == "failed"

    def test_llm_json_in_markdown_fence(self):
        fenced = f"```json\n{SAMPLE_LLM_RESPONSE}\n```"
        agent = ResumeAgentLLM(_make_context(llm_response=fenced))
        result = agent.execute({"resume_text": "text"})
        assert result.status.value == "completed"
        assert "python" in result.output["skills"]

    def test_respects_tool_budget(self):
        ctx = _make_context(llm_response=SAMPLE_LLM_RESPONSE)
        ctx.budgets = AgentBudgets(max_tool_calls=0)
        agent = ResumeAgentLLM(ctx)
        result = agent.execute({"resume_text": "text"})
        assert result.status.value == "failed"

    def test_agent_declares_only_llm_analyzer(self):
        assert ResumeAgentLLM.allowed_tools == frozenset({"llm_analyzer"})

    def test_agent_is_registered(self):
        assert AgentRegistry.get("resume_agent_llm") is ResumeAgentLLM
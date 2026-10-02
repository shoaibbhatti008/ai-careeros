"""
Basic agent usage example.

Run from project root:
    python docs/examples/basic_agent_usage.py
"""

import sys
from pathlib import Path
from uuid import uuid4

BACKEND = Path(__file__).resolve().parent.parent.parent / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from agents.context import AgentBudgets, AgentContext
from agents.implementations.resume_agent import ResumeAgent
from agents.tools.base import ToolContext
from agents.tools.career.resume_reader import ResumeReaderTool
from agents.tools.career.skill_extractor import SkillExtractorTool
from agents.tools.registry import ToolRegistry, execute_tool


def main() -> None:
    ToolRegistry._tools.setdefault("resume_reader", ResumeReaderTool)
    ToolRegistry._tools.setdefault("skill_extractor", SkillExtractorTool)

    user_id = uuid4()

    def tool_executor(tool_name: str, **kwargs: object) -> dict:
        return execute_tool(
            tool_name=tool_name,
            agent_name="resume_agent",
            agent_allowed_tools=ResumeAgent.allowed_tools,
            context_allowed_tools=frozenset({"resume_reader", "skill_extractor"}),
            input_data=dict(kwargs),
            tool_context=ToolContext(user_id=str(user_id)),
        )

    context = AgentContext(
        user_id=user_id,
        allowed_tools=frozenset({"resume_reader", "skill_extractor"}),
        tool_executor=tool_executor,
        budgets=AgentBudgets(max_steps=10, max_tool_calls=20),
    )

    agent = ResumeAgent(context)
    result = agent.execute(
        {
            "resume_text": (
                "John Doe\n"
                "Senior Software Engineer\n"
                "Experience\n"
                "- 5 years of Python and Django\n"
                "- PostgreSQL, Docker, Kubernetes on AWS\n"
                "Education\n"
                "BS Computer Science\n"
                "Skills\n"
                "Python, Django, PostgreSQL, Docker, Kubernetes, AWS\n"
            ),
            "target_role": "Backend Engineer",
        }
    )

    print("=" * 60)
    print("AGENT RESULT")
    print("=" * 60)
    print(f"Status:         {result.status.value}")
    print(f"Summary:        {result.summary}")
    print(f"Skills found:   {result.output.get('skills', [])}")
    print(f"Strengths:      {result.output.get('strengths', [])}")
    print(f"Improvements:   {result.output.get('improvements', [])}")
    print(f"ATS hints:      {result.output.get('ats_hints', [])}")
    print(f"Usage:          {result.usage}")
    print("=" * 60)


if __name__ == "__main__":
    main()
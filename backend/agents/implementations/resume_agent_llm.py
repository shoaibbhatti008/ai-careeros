"""
ResumeAgentLLM: LLM-powered resume analysis.

Falls back to the heuristic ResumeAgent if no LLM provider is available.
"""

from typing import Any

from agents.base import BaseAgent
from agents.registry import register_agent
from agents.result import AgentResult


@register_agent
class ResumeAgentLLM(BaseAgent):
    """
    LLM-powered resume analyzer.

    Uses the `llm_analyzer` tool with the `resume_analysis` prompt.
    The agent does NOT call the LLM directly — it uses the tool.

    The LLM provider is injected into ToolContext.metadata['llm_provider']
    by the caller. If missing, the tool returns an error and the agent
    returns a failed result.
    """

    name = "resume_agent_llm"
    description = "Analyzes resumes using an LLM (falls back to heuristics)."
    allowed_tools = frozenset({"llm_analyzer"})

    input_schema = {
        "type": "object",
        "properties": {
            "resume_text": {"type": "string"},
            "target_role": {"type": "string"},
        },
        "required": ["resume_text"],
    }

    output_schema = {
        "type": "object",
        "properties": {
            "skills": {"type": "array"},
            "strengths": {"type": "array"},
            "improvements": {"type": "array"},
            "ats_hints": {"type": "array"},
            "seniority_estimate": {"type": "string"},
            "target_role_fit": {"type": ["string", "null"]},
        },
    }

    def run(self, input_data: dict[str, Any]) -> AgentResult:
        resume_text = input_data.get("resume_text", "").strip()
        target_role = input_data.get("target_role", "").strip() or "(not specified)"

        if not resume_text:
            return AgentResult.failed("resume_text is required and cannot be empty.")

        # Call the LLM analyzer tool
        output = self.call_tool(
            "llm_analyzer",
            prompt_name="resume_analysis",
            template_vars={
                "resume_text": resume_text,
                "target_role": target_role,
            },
        )

        # Normalize output shape (defensive)
        normalized = {
            "skills": output.get("skills", []),
            "strengths": output.get("strengths", []),
            "improvements": output.get("improvements", []),
            "ats_hints": output.get("ats_hints", []),
            "seniority_estimate": output.get("seniority_estimate", "unknown"),
            "target_role_fit": output.get("target_role_fit"),
        }

        return AgentResult.completed(
            output=normalized,
            summary=(
                f"LLM analysis: {len(normalized['skills'])} skills, "
                f"{len(normalized['improvements'])} improvements suggested."
            ),
            usage={
                "steps": self.context.usage.steps,
                "tool_calls": self.context.usage.tool_calls,
            },
        )

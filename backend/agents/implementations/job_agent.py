"""
JobAgent: analyzes a job description and computes match against candidate skills.

The agent:
1. Parses the job description into structured fields
2. Extracts required skills from the job text
3. Matches against candidate skills
4. Returns a structured match analysis

The agent does NOT call an LLM directly. If an LLM provider is available,
it can additionally produce a human-readable explanation via the
llm_analyzer tool (but that's optional — heuristics work standalone).
"""

from typing import Any

from agents.base import BaseAgent
from agents.registry import register_agent
from agents.result import AgentResult


@register_agent
class JobAgent(BaseAgent):
    """Analyzes jobs and computes match against candidate skills."""

    name = "job_agent"
    description = "Parses job descriptions and matches them to candidate skills."
    allowed_tools = frozenset({"job_parser", "skill_extractor", "skill_matcher"})

    input_schema = {
        "type": "object",
        "properties": {
            "job_text": {"type": "string"},
            "candidate_skills": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["job_text"],
    }

    output_schema = {
        "type": "object",
        "properties": {
            "role_title": {"type": "string"},
            "seniority": {"type": "string"},
            "remote_policy": {"type": "string"},
            "required_skills": {"type": "array"},
            "matched_skills": {"type": "array"},
            "missing_skills": {"type": "array"},
            "extra_skills": {"type": "array"},
            "match_score": {"type": "number"},
        },
    }

    def run(self, input_data: dict[str, Any]) -> AgentResult:
        job_text = input_data.get("job_text", "").strip()
        candidate_skills = input_data.get("candidate_skills", []) or []

        if not job_text:
            return AgentResult.failed("job_text is required and cannot be empty.")

        # 1. Parse job description
        parsed = self.call_tool("job_parser", job_text=job_text)

        # 2. Extract required skills from the job text
        skills_result = self.call_tool("skill_extractor", text=job_text)
        required_skills = skills_result.get("skills", [])

        # 3. Match against candidate skills
        match = self.call_tool(
            "skill_matcher",
            candidate_skills=candidate_skills,
            required_skills=required_skills,
        )

        output = {
            "role_title": parsed.get("role_title", ""),
            "company": parsed.get("company", ""),
            "location": parsed.get("location", ""),
            "seniority": parsed.get("seniority", "unknown"),
            "remote_policy": parsed.get("remote_policy", "unknown"),
            "required_skills": required_skills,
            "matched_skills": match.get("matched", []),
            "missing_skills": match.get("missing", []),
            "extra_skills": match.get("extra", []),
            "match_score": match.get("match_score", 0.0),
        }

        return AgentResult.completed(
            output=output,
            summary=(
                f"Job: {output['role_title'] or 'unknown role'} "
                f"({output['seniority']}). "
                f"Match score: {output['match_score']:.0%} "
                f"({len(output['matched_skills'])} of "
                f"{len(required_skills)} skills)."
            ),
            usage={
                "steps": self.context.usage.steps,
                "tool_calls": self.context.usage.tool_calls,
            },
        )

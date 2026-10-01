"""
ResumeAgent: analyzes resumes and returns structured feedback.

The agent:
1. Reads resume text via the resume_reader tool
2. Extracts skills via the skill_extractor tool
3. Produces structured analysis with:
   - skills found
   - strength areas
   - improvement suggestions
   - ATS-compatibility hints

Design:
- Pure: receives input dict, returns AgentResult
- No DB access; all data passed via tools
- LLM optional: if no provider is available, falls back to heuristics
- Output strictly structured (validated)
"""

from typing import Any

from agents.base import BaseAgent
from agents.registry import register_agent
from agents.result import AgentResult


@register_agent
class ResumeAgent(BaseAgent):
    """Analyzes a resume and returns structured feedback."""

    name = "resume_agent"
    description = "Analyzes resumes for skills, strengths, and improvement areas."
    allowed_tools = frozenset({"resume_reader", "skill_extractor"})

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
            "skills": {"type": "array", "items": {"type": "string"}},
            "strengths": {"type": "array", "items": {"type": "string"}},
            "improvements": {"type": "array", "items": {"type": "string"}},
            "ats_hints": {"type": "array", "items": {"type": "string"}},
            "word_count": {"type": "integer"},
        },
    }

    def run(self, input_data: dict[str, Any]) -> AgentResult:
        resume_text = input_data.get("resume_text", "").strip()
        target_role = input_data.get("target_role", "").strip()

        if not resume_text:
            return AgentResult.failed("resume_text is required and cannot be empty.")

        # ---- Step 1: Read the resume ----
        read_result = self.call_tool(
            "resume_reader",
            resume_text=resume_text,
        )

        # ---- Step 2: Extract skills ----
        skills_result = self.call_tool(
            "skill_extractor",
            text=resume_text,
        )

        skills = skills_result.get("skills", [])
        word_count = read_result.get("word_count", 0)

        # ---- Step 3: Compute heuristics ----
        strengths: list[str] = []
        improvements: list[str] = []
        ats_hints: list[str] = []

        if word_count >= 200:
            strengths.append("Resume has substantial content.")
        elif word_count < 100:
            improvements.append("Resume is very short; add more detail.")

        if len(skills) >= 5:
            strengths.append(f"Resume lists {len(skills)} distinct skills.")
        else:
            improvements.append("Add more technical skills (aim for at least 5-10).")

        # Basic ATS heuristics
        lower_text = resume_text.lower()
        if "experience" not in lower_text:
            ats_hints.append("Add an 'Experience' section heading for ATS parsers.")
        if "education" not in lower_text:
            ats_hints.append("Add an 'Education' section heading.")
        if "skills" not in lower_text:
            ats_hints.append("Add a dedicated 'Skills' section.")

        if target_role:
            lower_role = target_role.lower()
            if lower_role.split()[0] not in lower_text:
                improvements.append(f"Tailor resume to mention '{target_role}' explicitly.")

        output = {
            "skills": skills,
            "strengths": strengths,
            "improvements": improvements,
            "ats_hints": ats_hints,
            "word_count": word_count,
            "target_role": target_role or None,
        }

        return AgentResult.completed(
            output=output,
            summary=(f"Analyzed resume with {len(skills)} skills and " f"{word_count} words."),
            usage={
                "steps": self.context.usage.steps,
                "tool_calls": self.context.usage.tool_calls,
            },
        )

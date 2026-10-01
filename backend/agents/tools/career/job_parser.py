"""
JobParserTool: extracts structured data from a job description.

Risk: LOW. Deterministic text parsing. No external access.

Note: This is a heuristic parser. An LLM-powered version can be added
later (see job_description_analysis prompt).
"""

import re
from typing import Any, ClassVar

from agents.tools.base import BaseTool, RiskLevel

# Common seniority keywords
SENIORITY_KEYWORDS = {
    "junior": ["junior", "entry level", "entry-level", "intern", "graduate"],
    "mid": ["mid-level", "mid level", "intermediate"],
    "senior": ["senior", "lead", "principal", "staff", "sr."],
    "unknown": [],
}


class JobParserTool(BaseTool):
    """Extract structured fields from a raw job description."""

    name = "job_parser"
    description = "Parses a job description into structured fields."
    risk_level: ClassVar[RiskLevel] = RiskLevel.LOW
    allowed_agents: ClassVar[frozenset[str]] = frozenset({"job_agent"})
    input_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {"job_text": {"type": "string"}},
        "required": ["job_text"],
    }
    output_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "role_title": {"type": "string"},
            "company": {"type": "string"},
            "location": {"type": "string"},
            "seniority": {"type": "string"},
            "remote_policy": {"type": "string"},
            "word_count": {"type": "integer"},
        },
    }
    timeout_seconds = 5
    rate_limit_per_minute = 300

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        text = input_data["job_text"]
        lower = text.lower()

        # Seniority detection
        seniority = "unknown"
        for level, keywords in SENIORITY_KEYWORDS.items():
            if level == "unknown":
                continue
            if any(kw in lower for kw in keywords):
                seniority = level
                break

        # Remote policy
        remote_policy = "unknown"
        if "remote" in lower and "hybrid" not in lower:
            remote_policy = "remote"
        elif "hybrid" in lower:
            remote_policy = "hybrid"
        elif "on-site" in lower or "onsite" in lower or "in office" in lower:
            remote_policy = "onsite"

        # Role title — first non-empty line, or first line before "at"
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        role_title = lines[0][:200] if lines else ""

        # Company — look for "at Company" or "Company is hiring"
        company = ""
        at_match = re.search(r"\bat\s+([A-Z][A-Za-z0-9&\.\- ]{1,60})", text)
        if at_match:
            company = at_match.group(1).strip()

        # Location — look for common patterns
        location = ""
        loc_match = re.search(r"\b(?:in|location:)\s+([A-Z][A-Za-z0-9 ,\-]{1,80})", text)
        if loc_match:
            location = loc_match.group(1).strip()

        return {
            "role_title": role_title,
            "company": company,
            "location": location,
            "seniority": seniority,
            "remote_policy": remote_policy,
            "word_count": len(text.split()),
        }

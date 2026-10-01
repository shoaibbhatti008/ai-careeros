"""
SkillExtractorTool: extracts known skills from free text.

Risk: LOW. Deterministic matching. No LLM, no network.
"""

from typing import Any, ClassVar

from agents.tools.base import BaseTool, RiskLevel

# A small starter catalog. In later phases this is backed by the DB.
DEFAULT_SKILL_CATALOG: frozenset[str] = frozenset(
    {
        # Languages
        "python",
        "javascript",
        "typescript",
        "java",
        "go",
        "rust",
        "c",
        "c++",
        "c#",
        "ruby",
        "php",
        "kotlin",
        "swift",
        "scala",
        # Web frameworks
        "django",
        "flask",
        "fastapi",
        "react",
        "vue",
        "angular",
        "next.js",
        "node.js",
        "express",
        # Databases
        "postgresql",
        "mysql",
        "sqlite",
        "mongodb",
        "redis",
        "elasticsearch",
        # DevOps
        "docker",
        "kubernetes",
        "aws",
        "gcp",
        "azure",
        "terraform",
        "ansible",
        "jenkins",
        "github actions",
        "ci/cd",
        # Data / AI
        "pandas",
        "numpy",
        "pytorch",
        "tensorflow",
        "scikit-learn",
        "machine learning",
        "deep learning",
        "nlp",
        "llm",
        "rag",
        # Tools
        "git",
        "linux",
        "bash",
        "rest",
        "graphql",
        "grpc",
    }
)


class SkillExtractorTool(BaseTool):
    """Extract known skills from free text using deterministic matching."""

    name = "skill_extractor"
    description = "Extracts known skills from text using a fixed catalog."
    risk_level: ClassVar[RiskLevel] = RiskLevel.LOW
    allowed_agents: ClassVar[frozenset[str]] = frozenset(
        {"resume_agent", "resume_agent_llm", "job_agent"}
    )
    input_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {"text": {"type": "string"}},
        "required": ["text"],
    }
    output_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "skills": {"type": "array", "items": {"type": "string"}},
        },
    }
    timeout_seconds = 5
    rate_limit_per_minute = 300

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        text = input_data["text"].lower()
        # Tokenize on word boundaries to avoid false positives
        import re

        tokens = set(re.findall(r"[a-z0-9\.\+\#/]+", text))
        found = sorted(skill for skill in DEFAULT_SKILL_CATALOG if skill in tokens)
        return {"skills": found}

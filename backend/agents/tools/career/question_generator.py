"""
QuestionGeneratorTool: generates mock interview questions.

Risk: LOW. Deterministic templates. No external access, no LLM.

The tool produces a mix of behavioral, technical, and system-design
questions based on the target role and skills.
"""

from typing import Any, ClassVar

from agents.tools.base import BaseTool, RiskLevel

# Behavioral question templates
BEHAVIORAL_TEMPLATES = [
    "Tell me about a time you handled a difficult technical challenge.",
    "Describe a situation where you disagreed with a teammate. How did you handle it?",
    "Give an example of a project you led from start to finish.",
    "Tell me about a time you had to learn a new technology quickly.",
    "Describe a time you made a mistake. What did you learn?",
    "Tell me about a time you mentored someone.",
    "Describe a situation where you had to prioritize competing demands.",
]

# System design templates
SYSTEM_DESIGN_TEMPLATES = [
    "How would you design a URL shortener that handles millions of requests per day?",
    "Design a real-time chat system for 1 million concurrent users.",
    "How would you design a rate limiter for an API?",
    "Design a job-matching system that ranks candidates for a role.",
    "How would you design a distributed task queue?",
]

# Technical question templates (skill-specific)
TECHNICAL_TEMPLATES: dict[str, list[str]] = {
    "python": [
        "Explain the difference between list and tuple in Python.",
        "What are Python generators and when would you use them?",
        "How does the GIL affect multi-threading in Python?",
    ],
    "django": [
        "Explain the Django request/response cycle.",
        "How do Django signals work? When would you use them?",
        "What is the difference between select_related and prefetch_related?",
    ],
    "postgresql": [
        "What is the difference between an index and a unique constraint?",
        "How would you optimize a slow query?",
        "Explain ACID properties.",
    ],
    "docker": [
        "What is the difference between a Docker image and a container?",
        "How do you reduce Docker image size?",
        "Explain Docker networking modes.",
    ],
    "kubernetes": [
        "What is a Kubernetes pod and how is it different from a container?",
        "Explain the difference between a Deployment and a StatefulSet.",
        "How does a Kubernetes Service route traffic to pods?",
    ],
    "react": [
        "Explain the difference between state and props in React.",
        "What are React hooks and why were they introduced?",
        "How does React's virtual DOM work?",
    ],
}

DEFAULT_TECHNICAL = [
    "Walk me through a complex technical project you've worked on.",
    "How do you approach debugging a production issue?",
    "Describe your testing strategy for a new feature.",
]


class QuestionGeneratorTool(BaseTool):
    """
    Generate mock interview questions.

    Input:
        target_role:  str (e.g. "Senior Backend Engineer")
        skills:       list[str]  (skills to focus on)
        count:        int (total questions to generate, default 5)

    Output:
        questions: list of {
            text: str,
            type: "behavioral" | "technical" | "system_design",
            skill: str | null,
            expected_topics: list[str],
        }
    """

    name = "question_generator"
    description = "Generates mock interview questions for a target role."
    risk_level: ClassVar[RiskLevel] = RiskLevel.LOW
    allowed_agents: ClassVar[frozenset[str]] = frozenset({"interview_agent"})
    input_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "target_role": {"type": "string"},
            "skills": {"type": "array", "items": {"type": "string"}},
            "count": {"type": "integer"},
        },
        "required": ["target_role"],
    }
    output_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "questions": {"type": "array"},
        },
    }
    timeout_seconds = 5
    rate_limit_per_minute = 100

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        input_data.get("target_role", "").strip()
        skills = [s.lower().strip() for s in input_data.get("skills", []) if s]
        count = int(input_data.get("count", 5))
        count = max(1, min(count, 20))  # clamp between 1 and 20

        questions: list[dict[str, Any]] = []

        # 1. Technical questions from skills (if any)
        for skill in skills:
            templates = TECHNICAL_TEMPLATES.get(skill, [])
            for q in templates[:1]:  # one per skill
                questions.append(
                    {
                        "text": q,
                        "type": "technical",
                        "skill": skill,
                        "expected_topics": [skill],
                    }
                )

        # 2. Fill remaining with behavioral + system design
        behavioral_idx = 0
        system_idx = 0
        while len(questions) < count:
            if len(questions) % 3 == 2:
                # every 3rd: system design
                q = SYSTEM_DESIGN_TEMPLATES[system_idx % len(SYSTEM_DESIGN_TEMPLATES)]
                system_idx += 1
                questions.append(
                    {
                        "text": q,
                        "type": "system_design",
                        "skill": None,
                        "expected_topics": ["scalability", "trade-offs"],
                    }
                )
            else:
                q = BEHAVIORAL_TEMPLATES[behavioral_idx % len(BEHAVIORAL_TEMPLATES)]
                behavioral_idx += 1
                questions.append(
                    {
                        "text": q,
                        "type": "behavioral",
                        "skill": None,
                        "expected_topics": ["communication", "impact"],
                    }
                )

        # Trim to count
        questions = questions[:count]

        # If we still have too few (edge case), fill with defaults
        while len(questions) < count:
            q = DEFAULT_TECHNICAL[len(questions) % len(DEFAULT_TECHNICAL)]
            questions.append(
                {
                    "text": q,
                    "type": "technical",
                    "skill": None,
                    "expected_topics": ["problem solving"],
                }
            )

        return {"questions": questions[:count]}

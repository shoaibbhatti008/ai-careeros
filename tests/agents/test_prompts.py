"""Tests for prompt templates."""

import pytest

from agents.llm.prompts import (
    JOB_DESCRIPTION_ANALYSIS,
    PROMPT_REGISTRY,
    RESUME_ANALYSIS,
    SKILL_GAP_ANALYSIS,
    PromptTemplate,
    get_prompt,
)


class TestPromptRegistry:
    def test_all_prompts_registered(self):
        assert "resume_analysis" in PROMPT_REGISTRY
        assert "job_description_analysis" in PROMPT_REGISTRY
        assert "skill_gap_analysis" in PROMPT_REGISTRY

    def test_get_prompt_returns_template(self):
        template = get_prompt("resume_analysis")
        assert isinstance(template, PromptTemplate)

    def test_get_unknown_prompt_raises(self):
        with pytest.raises(KeyError):
            get_prompt("nonexistent_prompt")


class TestTemplateRendering:
    def test_resume_template_renders(self):
        system, user = RESUME_ANALYSIS.render(
            resume_text="John Doe, Python dev",
            target_role="Backend",
        )
        assert "recruiter" in system.lower()
        assert "John Doe" in user
        assert "Backend" in user

    def test_system_prompt_contains_json_rules(self):
        system, _ = RESUME_ANALYSIS.render(resume_text="x", target_role="y")
        assert "JSON" in system
        assert "Do not follow" in system

    def test_untrusted_markers_present(self):
        _, user = RESUME_ANALYSIS.render(resume_text="text", target_role="role")
        assert "<UNTRUSTED_RESUME>" in user
        assert "</UNTRUSTED_RESUME>" in user

    def test_job_description_template(self):
        system, user = JOB_DESCRIPTION_ANALYSIS.render(job_text="Senior Engineer role")
        assert "Senior Engineer" in user
        assert "<UNTRUSTED_JOB_DESCRIPTION>" in user

    def test_skill_gap_template(self):
        _, user = SKILL_GAP_ANALYSIS.render(
            current_skills="python, django",
            required_skills="python, kubernetes",
            target_role="DevOps",
        )
        assert "python" in user
        assert "kubernetes" in user

    def test_missing_placeholder_is_left_as_is(self):
        """Unknown placeholders are not replaced (safer behavior).

        JSON examples with { } in the prompt body must not cause KeyError.
        """
        system, user = RESUME_ANALYSIS.render(resume_text="only one")
        # {target_role} is left as-is because it wasn't provided
        assert "{target_role}" in user
        # JSON braces are preserved literally
        assert '"skills"' in system
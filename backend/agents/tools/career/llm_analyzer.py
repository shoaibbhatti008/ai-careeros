"""
LLMAnalyzerTool: calls an LLM to analyze text.

Risk: MEDIUM (external API call). Requires an injected LLM provider.
The tool NEVER sends raw user data to the LLM without prompt-guard screening.

The provider is injected via ToolContext.metadata["llm_provider"].
"""

from typing import Any, ClassVar

from agents.llm.json_parser import parse_json_from_llm
from agents.llm.prompts import PromptTemplate
from agents.tools.base import BaseTool, RiskLevel


class LLMAnalyzerTool(BaseTool):
    """
    Call an LLM with a registered prompt template and return parsed JSON.

    Input:
        prompt_name: which template to use
        template_vars: dict of placeholder values

    Output:
        Parsed JSON dict from the LLM response.
    """

    name = "llm_analyzer"
    description = "Calls an LLM with a registered prompt and returns structured JSON."
    risk_level: ClassVar[RiskLevel] = RiskLevel.MEDIUM
    allowed_agents: ClassVar[frozenset[str]] = frozenset({"resume_agent_llm"})
    input_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
        "properties": {
            "prompt_name": {"type": "string"},
            "template_vars": {"type": "object"},
        },
        "required": ["prompt_name", "template_vars"],
    }
    output_schema: ClassVar[dict[str, Any]] = {
        "type": "object",
    }
    timeout_seconds = 60
    rate_limit_per_minute = 30
    requires_approval = False  # LLM analysis is not sensitive enough

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        provider = self.context.metadata.get("llm_provider")
        if provider is None:
            from agents.exceptions import AgentProviderError

            raise AgentProviderError(
                "No LLM provider was injected into ToolContext.metadata['llm_provider']."
            )

        prompt_name = input_data["prompt_name"]
        template_vars = input_data["template_vars"]

        # Resolve template
        from agents.llm.prompts import get_prompt

        try:
            template: PromptTemplate = get_prompt(prompt_name)
        except KeyError as exc:
            from agents.tools.errors import ToolInputError

            raise ToolInputError(
                f"Unknown prompt template: {prompt_name}",
                tool_name=self.name,
            ) from exc

        system_prompt, user_prompt = template.render(**template_vars)

        # Call the LLM
        try:
            response = provider.complete(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )
        except Exception as exc:
            from agents.tools.errors import ToolExecutionError

            raise ToolExecutionError(
                f"LLM call failed: {exc}",
                tool_name=self.name,
            ) from exc

        # Parse JSON
        try:
            return parse_json_from_llm(response.content)
        except Exception as exc:
            from agents.tools.errors import ToolOutputError

            raise ToolOutputError(
                f"LLM returned non-JSON content: {exc}",
                tool_name=self.name,
            ) from exc

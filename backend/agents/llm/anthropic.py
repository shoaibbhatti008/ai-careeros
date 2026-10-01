"""
Anthropic LLM provider.

Requires:
    pip install anthropic
    ANTHROPIC_API_KEY (or AI_API_KEY) environment variable
"""

from typing import Any

from agents.exceptions import AgentProviderError
from agents.llm.provider import LLMProvider, LLMResponse

try:
    from anthropic import Anthropic  # type: ignore

    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False
    Anthropic = None  # type: ignore


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    DEFAULT_MODEL = "claude-3-5-haiku-latest"

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        timeout: float = 60.0,
    ) -> None:
        if not _ANTHROPIC_AVAILABLE:
            raise AgentProviderError("Anthropic SDK is not installed. Run: pip install anthropic")
        if not api_key:
            raise AgentProviderError("Anthropic API key is required.")

        self._model = model
        self._client = Anthropic(api_key=api_key, timeout=timeout)

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def complete(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int = 2048,
        **kwargs: Any,
    ) -> LLMResponse:
        try:
            response = self._client.messages.create(
                model=model or self._model,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
        except Exception as exc:
            raise AgentProviderError(f"Anthropic call failed: {exc}") from exc

        # Anthropic returns a list of content blocks
        content = ""
        for block in response.content:
            if hasattr(block, "text"):
                content += block.text

        return LLMResponse(
            content=content,
            model=response.model,
            prompt_tokens=response.usage.input_tokens,
            completion_tokens=response.usage.output_tokens,
            finish_reason=response.stop_reason or "stop",
            raw={"id": response.id},
        )

    def is_available(self) -> bool:
        return _ANTHROPIC_AVAILABLE

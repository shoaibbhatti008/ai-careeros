"""
OpenAI LLM provider.

Requires:
    pip install openai
    OPENAI_API_KEY (or AI_API_KEY) environment variable

The provider is optional — if the SDK is not installed or the API key
is missing, `is_available()` returns False and calls raise AgentProviderError.
"""

from typing import Any

from agents.exceptions import AgentProviderError
from agents.llm.provider import LLMProvider, LLMResponse

try:
    from openai import OpenAI  # type: ignore

    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False
    OpenAI = None  # type: ignore


class OpenAIProvider(LLMProvider):
    """
    OpenAI LLM provider.

    Usage:
        provider = OpenAIProvider(api_key="sk-...")
        response = provider.complete(
            system_prompt="You are a helpful assistant.",
            user_prompt="Hello!",
        )
    """

    DEFAULT_MODEL = "gpt-4o-mini"

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        organization: str | None = None,
        base_url: str | None = None,
        timeout: float = 60.0,
    ) -> None:
        if not _OPENAI_AVAILABLE:
            raise AgentProviderError("OpenAI SDK is not installed. Run: pip install openai")
        if not api_key:
            raise AgentProviderError("OpenAI API key is required.")

        self._model = model
        self._client = OpenAI(
            api_key=api_key,
            organization=organization,
            base_url=base_url,
            timeout=timeout,
        )

    @property
    def provider_name(self) -> str:
        return "openai"

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
            response = self._client.chat.completions.create(
                model=model or self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
        except Exception as exc:
            raise AgentProviderError(f"OpenAI call failed: {exc}") from exc

        choice = response.choices[0]
        usage = response.usage
        return LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            prompt_tokens=usage.prompt_tokens if usage else 0,
            completion_tokens=usage.completion_tokens if usage else 0,
            finish_reason=choice.finish_reason or "stop",
            raw={"id": response.id},
        )

    def is_available(self) -> bool:
        return _OPENAI_AVAILABLE

"""
Mock LLM provider for testing.

Deterministic, no network, no cost.
"""

from typing import Any

from backend.agents.llm.provider import LLMProvider, LLMResponse


class MockLLMProvider(LLMProvider):
    """
    Deterministic mock provider.

    Usage in tests:
        provider = MockLLMProvider(default_response='{"skills": ["python"]}')
        response = provider.complete(system_prompt="...", user_prompt="...")
        assert response.content == '{"skills": ["python"]}'
    """

    def __init__(
        self,
        default_response: str = "mock response",
        responses: list[str] | None = None,
    ) -> None:
        self._default = default_response
        self._queue = list(responses or [])
        self.calls: list[dict[str, Any]] = []

    @property
    def provider_name(self) -> str:
        return "mock"

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
        self.calls.append(
            {
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
        )
        content = self._queue.pop(0) if self._queue else self._default
        return LLMResponse(
            content=content,
            model=model or "mock-model",
            prompt_tokens=10,
            completion_tokens=20,
            finish_reason="stop",
        )

    def is_available(self) -> bool:
        return True

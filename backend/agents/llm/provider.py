"""
Provider-agnostic LLM interface.

Implementations:
- MockLLMProvider (for tests)
- OpenAIProvider (Phase 7B)
- AnthropicProvider (Phase 7B)
- AzureOpenAIProvider (Phase 7B)
- OllamaProvider (Phase 7B)

Agents depend on this interface, NOT on a specific SDK.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class LLMResponse:
    """Structured response from an LLM provider."""

    content: str
    model: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    finish_reason: str = "stop"
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


class LLMProvider(ABC):
    """
    Abstract LLM provider.

    Implementations wrap a specific vendor SDK (OpenAI, Anthropic, etc.)
    and expose a stable, minimal interface.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider name (e.g. 'openai', 'anthropic')."""
        raise NotImplementedError

    @abstractmethod
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
        """
        Single-turn completion.

        Args:
            system_prompt: system instructions
            user_prompt:   user content
            model:         model override
            temperature:   sampling temperature
            max_tokens:    token limit

        Returns:
            LLMResponse
        """
        raise NotImplementedError

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this provider is configured and reachable."""
        raise NotImplementedError

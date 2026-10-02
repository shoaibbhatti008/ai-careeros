"""
LLM provider factory.

Reads environment variables and returns the appropriate provider.
"""

import os

from agents.exceptions import AgentProviderError
from agents.llm.anthropic import AnthropicProvider
from agents.llm.groq import GroqProvider
from agents.llm.mock import MockLLMProvider
from agents.llm.openai import OpenAIProvider
from agents.llm.provider import LLMProvider


def get_provider(name: str | None = None) -> LLMProvider:
    """
    Return an LLM provider instance based on configuration.
    """
    provider_name = (name or os.environ.get("AI_PROVIDER", "mock")).lower()

    api_key = os.environ.get("AI_API_KEY", "")
    model = os.environ.get("AI_MODEL") or None
    timeout = float(os.environ.get("AI_TIMEOUT_SECONDS", "60"))

    if provider_name == "mock":
        return MockLLMProvider()

    if provider_name == "groq":
        if not api_key:
            raise AgentProviderError("AI_API_KEY is required for Groq.")
        kwargs: dict = {"api_key": api_key, "timeout": timeout}
        if model:
            kwargs["model"] = model
        return GroqProvider(**kwargs)

    if provider_name == "openai":
        if not api_key:
            raise AgentProviderError("AI_API_KEY is required for OpenAI.")
        kwargs = {"api_key": api_key, "timeout": timeout}
        if model:
            kwargs["model"] = model
        return OpenAIProvider(**kwargs)

    if provider_name == "anthropic":
        if not api_key:
            raise AgentProviderError("AI_API_KEY is required for Anthropic.")
        kwargs = {"api_key": api_key, "timeout": timeout}
        if model:
            kwargs["model"] = model
        return AnthropicProvider(**kwargs)

    raise AgentProviderError(f"Unknown AI_PROVIDER: {provider_name}")

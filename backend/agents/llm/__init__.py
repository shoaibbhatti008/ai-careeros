"""LLM provider-agnostic interface."""

from backend.agents.llm.mock import MockLLMProvider
from backend.agents.llm.provider import LLMProvider, LLMResponse

__all__ = ["LLMProvider", "LLMResponse", "MockLLMProvider"]

"""Tests for LLM providers."""

import os

import pytest

from agents.exceptions import AgentProviderError
from agents.llm import AnthropicProvider, MockLLMProvider, OpenAIProvider, get_provider
from agents.llm.factory import get_provider as factory_get_provider


class TestMockProvider:
    def test_default_response(self):
        p = MockLLMProvider(default_response="hello")
        r = p.complete(system_prompt="sys", user_prompt="user")
        assert r.content == "hello"
        assert p.provider_name == "mock"

    def test_queued_responses(self):
        p = MockLLMProvider(responses=["a", "b", "c"])
        assert p.complete(system_prompt="", user_prompt="").content == "a"
        assert p.complete(system_prompt="", user_prompt="").content == "b"
        assert p.complete(system_prompt="", user_prompt="").content == "c"

    def test_records_calls(self):
        p = MockLLMProvider()
        p.complete(system_prompt="S", user_prompt="U", model="x", temperature=0.5)
        assert len(p.calls) == 1
        assert p.calls[0]["system_prompt"] == "S"
        assert p.calls[0]["model"] == "x"

    def test_is_available(self):
        assert MockLLMProvider().is_available() is True

    def test_token_counting(self):
        p = MockLLMProvider()
        r = p.complete(system_prompt="", user_prompt="")
        assert r.total_tokens == 30  # 10 + 20 from mock


class TestFactory:
    def test_default_is_mock(self, monkeypatch):
        monkeypatch.delenv("AI_PROVIDER", raising=False)
        provider = factory_get_provider()
        assert provider.provider_name == "mock"

    def test_explicit_mock(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "mock")
        provider = factory_get_provider()
        assert provider.provider_name == "mock"

    def test_unknown_provider_raises(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "unknown_provider")
        with pytest.raises(AgentProviderError):
            factory_get_provider()

    def test_openai_requires_api_key(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "openai")
        monkeypatch.delenv("AI_API_KEY", raising=False)
        # If OpenAI SDK not installed, this raises AgentProviderError anyway
        with pytest.raises(AgentProviderError):
            factory_get_provider()

    def test_anthropic_requires_api_key(self, monkeypatch):
        monkeypatch.setenv("AI_PROVIDER", "anthropic")
        monkeypatch.delenv("AI_API_KEY", raising=False)
        with pytest.raises(AgentProviderError):
            factory_get_provider()
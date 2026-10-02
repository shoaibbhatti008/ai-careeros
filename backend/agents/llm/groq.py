"""
Groq LLM provider.

Groq provides fast, free-tier LLM inference using an OpenAI-compatible API.

Requires:
    pip install openai   (Groq uses the OpenAI SDK)

Environment:
    AI_API_KEY  — Groq API key (starts with `gsk_`)
    AI_MODEL    — model name (default: openai/gpt-oss-120b)
    FORCE_IPV4  — if "true", force IPv4 (helps on ISPs with broken IPv6)
"""

import socket
from typing import Any

from agents.exceptions import AgentProviderError
from agents.llm.provider import LLMProvider, LLMResponse

try:
    from openai import OpenAI  # type: ignore

    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False
    OpenAI = None  # type: ignore

import os

GROQ_BASE_URL = "https://api.groq.com/openai/v1"


def _force_ipv4() -> None:
    """
    Force Python's socket layer to prefer IPv4 over IPv6.

    This works around ISPs (common in Pakistan) that advertise IPv6
    addresses but don't actually route them.
    """
    # Override getaddrinfo to filter IPv6 results
    _original_getaddrinfo = socket.getaddrinfo

    def _ipv4_only_getaddrinfo(
        host: str,
        port: int,
        family: int = 0,
        type: int = 0,
        proto: int = 0,
        flags: int = 0,
    ) -> list:
        responses = _original_getaddrinfo(host, port, family, type, proto, flags)
        ipv4 = [r for r in responses if r[0] == socket.AF_INET]
        return ipv4 or responses  # fall back if no IPv4 available

    socket.getaddrinfo = _ipv4_only_getaddrinfo  # type: ignore


class GroqProvider(LLMProvider):
    """
    Groq LLM provider (OpenAI-compatible).

    Usage:
        provider = GroqProvider(api_key="gsk_...")
        response = provider.complete(
            system_prompt="You are a helpful assistant.",
            user_prompt="Hello!",
        )
    """

    DEFAULT_MODEL = "openai/gpt-oss-120b"

    def __init__(
        self,
        api_key: str,
        model: str = DEFAULT_MODEL,
        timeout: float = 60.0,
    ) -> None:
        if not _OPENAI_AVAILABLE:
            raise AgentProviderError("OpenAI SDK is not installed. Run: pip install openai")
        if not api_key:
            raise AgentProviderError("Groq API key is required.")

        # Force IPv4 if configured
        force_ipv4 = os.environ.get("FORCE_IPV4", "true").lower() in (
            "true",
            "1",
            "yes",
        )
        if force_ipv4:
            _force_ipv4()

        self._model = model
        self._client = OpenAI(
            api_key=api_key,
            base_url=GROQ_BASE_URL,
            timeout=timeout,
        )

    @property
    def provider_name(self) -> str:
        return "groq"

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
            raise AgentProviderError(f"Groq call failed: {exc}") from exc

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

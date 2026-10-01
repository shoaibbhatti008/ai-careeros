"""
Robust JSON parsing for LLM outputs.

LLMs sometimes return:
- Markdown code fences (```json ... ```)
- Trailing commas
- Leading/trailing prose
- Escaped unicode

This module attempts to extract clean JSON from such responses.
"""

import json
import re
from typing import Any

from agents.exceptions import AgentValidationError


def parse_json_from_llm(content: str) -> dict[str, Any]:
    """
    Extract and parse JSON from an LLM response.

    Tries (in order):
    1. Direct parse
    2. Strip markdown code fences (```json ... ```)
    3. Extract first {...} block and parse
    4. Remove trailing commas and retry

    Raises:
        AgentValidationError: if all attempts fail.
    """
    if not content or not content.strip():
        raise AgentValidationError("LLM returned empty content.")

    text = content.strip()

    # Attempt 1: direct parse
    result = _try_parse(text)
    if result is not None:
        return result

    # Attempt 2: strip markdown code fences
    fence_pattern = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)
    match = fence_pattern.search(text)
    if match:
        result = _try_parse(match.group(1).strip())
        if result is not None:
            return result

    # Attempt 3: extract first {...} block
    brace_pattern = re.compile(r"\{.*\}", re.DOTALL)
    match = brace_pattern.search(text)
    if match:
        result = _try_parse(match.group(0).strip())
        if result is not None:
            return result

        # Attempt 4: remove trailing commas and retry
        cleaned = _remove_trailing_commas(match.group(0))
        result = _try_parse(cleaned)
        if result is not None:
            return result

    raise AgentValidationError(
        f"Could not parse JSON from LLM response. " f"First 200 chars: {content[:200]!r}"
    )


def _try_parse(text: str) -> dict[str, Any] | None:
    """Try to parse text as a JSON object. Return None on failure."""
    try:
        parsed = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(parsed, dict):
        return None
    return parsed


def _remove_trailing_commas(text: str) -> str:
    """Remove trailing commas before } or ]."""
    return re.sub(r",(\s*[}\]])", r"\1", text)

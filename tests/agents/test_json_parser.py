"""Tests for robust JSON parsing."""

import pytest

from agents.exceptions import AgentValidationError
from agents.llm.json_parser import parse_json_from_llm


class TestJsonParser:
    def test_parses_direct_json(self):
        result = parse_json_from_llm('{"key": "value"}')
        assert result == {"key": "value"}

    def test_parses_json_with_markdown_fence(self):
        content = '```json\n{"key": "value"}\n```'
        result = parse_json_from_llm(content)
        assert result == {"key": "value"}

    def test_parses_json_with_plain_fence(self):
        content = '```\n{"key": "value"}\n```'
        result = parse_json_from_llm(content)
        assert result == {"key": "value"}

    def test_parses_json_with_surrounding_prose(self):
        content = 'Here is the analysis:\n{"key": "value"}\nHope this helps!'
        result = parse_json_from_llm(content)
        assert result == {"key": "value"}

    def test_removes_trailing_commas(self):
        content = '{"a": 1, "b": 2,}'
        result = parse_json_from_llm(content)
        assert result == {"a": 1, "b": 2}

    def test_nested_json(self):
        content = '{"outer": {"inner": [1, 2, 3]}}'
        result = parse_json_from_llm(content)
        assert result["outer"]["inner"] == [1, 2, 3]

    def test_empty_content_raises(self):
        with pytest.raises(AgentValidationError):
            parse_json_from_llm("")

    def test_whitespace_only_raises(self):
        with pytest.raises(AgentValidationError):
            parse_json_from_llm("   \n  ")

    def test_non_json_raises(self):
        with pytest.raises(AgentValidationError):
            parse_json_from_llm("This is not JSON at all.")

    def test_array_not_object_raises(self):
        with pytest.raises(AgentValidationError):
            parse_json_from_llm("[1, 2, 3]")

    def test_error_includes_preview(self):
        with pytest.raises(AgentValidationError) as exc_info:
            parse_json_from_llm("Bad content here")
        assert "Bad content" in str(exc_info.value)
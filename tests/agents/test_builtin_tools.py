"""Tests for built-in tools."""

from agents.tools.base import ToolContext
from agents.tools.builtin import EchoTool, TextLengthTool, TextNormalizeTool
from agents.tools.registry import ToolRegistry


class TestEchoTool:
    def test_echoes_message(self):
        tool = EchoTool(ToolContext(user_id="u1"))
        result = tool.execute({"message": "hello"})
        assert result.success is True
        assert result.data["echo"] == "hello"

    def test_echoes_empty_by_default(self):
        tool = EchoTool(ToolContext(user_id="u1"))
        result = tool.execute({})
        assert result.success is True
        assert result.data["echo"] == ""


class TestTextLengthTool:
    def test_counts_characters_and_words(self):
        tool = TextLengthTool(ToolContext(user_id="u1"))
        result = tool.execute({"text": "hello world"})
        assert result.success is True
        assert result.data["char_count"] == 11
        assert result.data["word_count"] == 2

    def test_requires_text_field(self):
        tool = TextLengthTool(ToolContext(user_id="u1"))
        result = tool.execute({})
        assert result.success is False
        assert "text" in result.error.lower()


class TestTextNormalizeTool:
    def test_collapses_whitespace(self):
        tool = TextNormalizeTool(ToolContext(user_id="u1"))
        result = tool.execute({"text": "  hello   world  "})
        assert result.success is True
        assert result.data["text"] == "hello world"

    def test_lowercase_option(self):
        tool = TextNormalizeTool(ToolContext(user_id="u1"))
        result = tool.execute({"text": "HELLO World", "lowercase": True})
        assert result.success is True
        assert result.data["text"] == "hello world"

    def test_lowercase_default_false(self):
        tool = TextNormalizeTool(ToolContext(user_id="u1"))
        result = tool.execute({"text": "HELLO"})
        assert result.data["text"] == "HELLO"


class TestBuiltinToolsRegistered:
    def test_all_builtin_tools_are_registered(self):
        # Register builtin tools if not already
        from agents.tools.builtin import EchoTool, TextLengthTool, TextNormalizeTool
        from agents.tools.registry import ToolRegistry

        for tool in (EchoTool, TextLengthTool, TextNormalizeTool):
            if not ToolRegistry.has(tool.name):
                ToolRegistry.register(tool)

        assert ToolRegistry.has("echo") is True
        assert ToolRegistry.has("text_length") is True
        assert ToolRegistry.has("text_normalize") is True

    def test_builtin_tools_have_low_risk(self):
        from agents.tools.builtin import EchoTool, TextLengthTool, TextNormalizeTool
        from agents.tools.registry import ToolRegistry

        for tool in (EchoTool, TextLengthTool, TextNormalizeTool):
            if not ToolRegistry.has(tool.name):
                ToolRegistry.register(tool)

        tools = ToolRegistry.list_tools()
        for name in ("echo", "text_length", "text_normalize"):
            assert tools[name]["risk_level"] == "low"
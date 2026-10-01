"""Tests for the verification layer."""

from uuid import uuid4

import pytest

from agents.context import AgentBudgets, AgentContext
from agents.implementations.verification_agent import VerificationAgent
from agents.registry import AgentRegistry
from agents.tools.base import ToolContext
from agents.tools.builtin.verify import VerifyOutputTool
from agents.tools.registry import ToolRegistry, execute_tool
from agents.verification.checks import (
    check_confidence,
    check_no_pii,
    check_no_placeholders,
    check_required_fields,
    check_schema,
)
from agents.verification.verifier import Verifier


# ==========================================================
# Check tests
# ==========================================================


class TestSchemaCheck:
    def test_valid_data_passes(self):
        result = check_schema(
            {"name": "Ali", "age": 30},
            {
                "type": "object",
                "required": ["name", "age"],
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                },
            },
        )
        assert result.passed is True

    def test_missing_required_field_fails(self):
        result = check_schema(
            {"name": "Ali"},
            {
                "type": "object",
                "required": ["name", "age"],
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                },
            },
        )
        assert result.passed is False
        assert "age" in result.message

    def test_wrong_type_fails(self):
        result = check_schema(
            {"age": "not a number"},
            {
                "type": "object",
                "properties": {"age": {"type": "integer"}},
            },
        )
        assert result.passed is False


class TestRequiredFieldsCheck:
    def test_all_present_passes(self):
        result = check_required_fields({"a": 1, "b": [1]}, ["a", "b"])
        assert result.passed is True

    def test_missing_field_fails(self):
        result = check_required_fields({"a": 1}, ["a", "b"])
        assert result.passed is False

    def test_empty_field_fails(self):
        result = check_required_fields({"a": [], "b": "ok"}, ["a", "b"])
        assert result.passed is False
        assert "a" in result.message

    def test_none_field_fails(self):
        result = check_required_fields({"a": None}, ["a"])
        assert result.passed is False


class TestPlaceholderCheck:
    def test_clean_data_passes(self):
        result = check_no_placeholders({"text": "Hello world"})
        assert result.passed is True

    def test_detects_dollar_placeholder(self):
        result = check_no_placeholders({"text": "Hello ${name}"})
        assert result.passed is False

    def test_detects_todo(self):
        result = check_no_placeholders({"text": "TODO: fix this"})
        assert result.passed is False

    def test_detects_nested(self):
        result = check_no_placeholders({"items": [{"t": "FIXME"}]})
        assert result.passed is False


class TestConfidenceCheck:
    def test_valid_confidence_passes(self):
        result = check_confidence(0.8)
        assert result.passed is True

    def test_below_min_fails(self):
        result = check_confidence(0.3, min_confidence=0.5)
        assert result.passed is False

    def test_out_of_range_fails(self):
        result = check_confidence(1.5)
        assert result.passed is False

    def test_none_is_warning(self):
        result = check_confidence(None)
        assert result.passed is True
        assert result.severity == "warning"


class TestPIICheck:
    def test_clean_data_passes(self):
        result = check_no_pii({"text": "no pii here"})
        assert result.passed is True

    def test_detects_ssn(self):
        result = check_no_pii({"text": "SSN: 123-45-6789"})
        assert result.passed is False

    def test_detects_email_by_default(self):
        result = check_no_pii({"text": "email me at foo@example.com"})
        assert result.passed is False

    def test_email_allowed_when_configured(self):
        result = check_no_pii(
            {"text": "email me at foo@example.com"},
            allow_emails=True,
        )
        assert result.passed is True


# ==========================================================
# Verifier tests
# ==========================================================


class TestVerifier:
    def test_passes_with_valid_data(self):
        v = Verifier(required_fields=["name"])
        report = v.verify({"name": "Ali"})
        assert report.passed is True

    def test_fails_with_missing_field(self):
        v = Verifier(required_fields=["name", "email"])
        report = v.verify({"name": "Ali"})
        assert report.passed is False
        assert report.has_errors

    def test_warnings_without_errors(self):
        v = Verifier(required_fields=[], min_confidence=0.0)
        report = v.verify({}, confidence=None)
        assert report.passed is True
        assert report.has_warnings

    def test_summary_reflects_status(self):
        v = Verifier(required_fields=["a"])
        report = v.verify({"a": "x"})
        assert "passed" in report.summary().lower()

    def test_schema_integration(self):
        v = Verifier(
            schema={
                "type": "object",
                "required": ["score"],
                "properties": {"score": {"type": "number"}},
            }
        )
        report = v.verify({"score": 0.7})
        assert report.passed is True

    def test_schema_failure_propagates(self):
        v = Verifier(
            schema={
                "type": "object",
                "required": ["score"],
                "properties": {"score": {"type": "number"}},
            }
        )
        report = v.verify({"score": "not a number"})
        assert report.passed is False


# ==========================================================
# VerificationAgent tests
# ==========================================================


@pytest.fixture(autouse=True)
def register_verification_agent():
    ToolRegistry._tools.setdefault("verify_output", VerifyOutputTool)
    AgentRegistry._agents.setdefault("verification_agent", VerificationAgent)
    yield


def _make_context(*, allowed_tools: frozenset[str] | None = None) -> AgentContext:
    if allowed_tools is None:
        tools = frozenset({"verify_output"})
    else:
        tools = allowed_tools

    def tool_executor(tool_name: str, **kwargs: object) -> dict:
        tool_context = ToolContext(user_id=str(uuid4()))
        return execute_tool(
            tool_name=tool_name,
            agent_name="verification_agent",
            agent_allowed_tools=VerificationAgent.allowed_tools,
            context_allowed_tools=tools,
            input_data=dict(kwargs),
            tool_context=tool_context,
        )

    return AgentContext(
        user_id=uuid4(),
        allowed_tools=tools,
        tool_executor=tool_executor,
    )


class TestVerificationAgent:
    def test_passes_valid_output(self):
        agent = VerificationAgent(_make_context())
        result = agent.execute(
            {
                "data": {"name": "Ali", "score": 0.9},
                "required_fields": ["name", "score"],
            }
        )
        assert result.status.value == "completed"
        assert result.output["passed"] is True

    def test_fails_missing_field(self):
        agent = VerificationAgent(_make_context())
        result = agent.execute(
            {
                "data": {"name": "Ali"},
                "required_fields": ["name", "score"],
            }
        )
        assert result.status.value == "failed"
        assert result.output["passed"] is False
        assert any("score" in e for e in result.output["errors"])

    def test_schema_validation(self):
        agent = VerificationAgent(_make_context())
        result = agent.execute(
            {
                "data": {"score": "text"},
                "schema": {
                    "type": "object",
                    "properties": {"score": {"type": "number"}},
                },
            }
        )
        assert result.status.value == "failed"

    def test_data_must_be_dict(self):
        agent = VerificationAgent(_make_context())
        result = agent.execute({"data": "not a dict"})
        assert result.status.value == "failed"

    def test_agent_is_registered(self):
        assert AgentRegistry.get("verification_agent") is VerificationAgent

    def test_agent_declares_one_tool(self):
        assert VerificationAgent.allowed_tools == frozenset({"verify_output"})

    def test_respects_allowlist(self):
        ctx = _make_context(allowed_tools=frozenset())
        agent = VerificationAgent(ctx)
        result = agent.execute({"data": {}})
        assert result.status.value == "failed"

    def test_respects_budget(self):
        ctx = _make_context()
        ctx.budgets = AgentBudgets(max_tool_calls=0)
        agent = VerificationAgent(ctx)
        result = agent.execute({"data": {}})
        assert result.status.value == "failed"

    def test_output_shape(self):
        agent = VerificationAgent(_make_context())
        result = agent.execute({"data": {"x": 1}})
        assert isinstance(result.output["passed"], bool)
        assert isinstance(result.output["errors"], list)
        assert isinstance(result.output["warnings"], list)
        assert isinstance(result.output["summary"], str)

    def test_pii_detection_by_default(self):
        agent = VerificationAgent(_make_context())
        result = agent.execute(
            {
                "data": {"note": "SSN 123-45-6789"},
            }
        )
        # PII is a warning, not an error by default
        assert result.output["passed"] is True
        assert any("pii" in w.lower() for w in result.output["warnings"])
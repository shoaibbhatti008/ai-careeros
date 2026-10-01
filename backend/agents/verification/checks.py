"""
Individual verification checks.

Each check is a pure function that takes data + config and returns
a CheckResult. Checks NEVER raise; they return a failed result.
"""

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CheckResult:
    """Result of a single check."""

    name: str
    passed: bool
    message: str = ""
    severity: str = "error"  # "info" | "warning" | "error"
    details: dict[str, Any] = field(default_factory=dict)


# ============================================================
# Schema / structure checks
# ============================================================


def check_schema(data: dict[str, Any], schema: dict[str, Any]) -> CheckResult:
    """
    Validate `data` against a minimal schema (types only).

    Supports: type, required, properties, items.
    """
    errors: list[str] = []
    _validate(data, schema, errors, path="")
    return CheckResult(
        name="schema",
        passed=len(errors) == 0,
        message="; ".join(errors) if errors else "Schema OK",
        details={"errors": errors},
    )


def _validate(
    data: Any,
    schema: dict[str, Any],
    errors: list[str],
    path: str,
) -> None:
    expected = schema.get("type")
    if expected is None:
        return

    if not _type_ok(data, expected):
        errors.append(f"{path or 'root'}: expected {expected}, got {type(data).__name__}")
        return

    if expected == "object":
        for field_name in schema.get("required", []):
            if field_name not in data:
                errors.append(f"{path or 'root'}: missing '{field_name}'")
        for field_name, field_schema in schema.get("properties", {}).items():
            if field_name in data:
                _validate(
                    data[field_name],
                    field_schema,
                    errors,
                    f"{path}.{field_name}" if path else field_name,
                )
    elif expected == "array":
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(data):
                _validate(item, item_schema, errors, f"{path}[{i}]")


def _type_ok(value: Any, expected: str) -> bool:
    if expected == "object":
        return isinstance(value, dict)
    if expected == "array":
        return isinstance(value, list)
    if expected == "string":
        return isinstance(value, str)
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if expected == "boolean":
        return isinstance(value, bool)
    if expected == "null":
        return value is None
    return True


# ============================================================
# Content checks
# ============================================================


def check_required_fields(
    data: dict[str, Any],
    required: list[str],
) -> CheckResult:
    """Check that all required top-level fields are present and non-empty."""
    missing: list[str] = []
    empty: list[str] = []

    for field_name in required:
        if field_name not in data:
            missing.append(field_name)
        else:
            value = data[field_name]
            if value is None:
                empty.append(field_name)
            elif isinstance(value, (str, list, dict)) and len(value) == 0:
                empty.append(field_name)

    passed = not missing and not empty
    parts: list[str] = []
    if missing:
        parts.append(f"missing: {', '.join(missing)}")
    if empty:
        parts.append(f"empty: {', '.join(empty)}")

    return CheckResult(
        name="required_fields",
        passed=passed,
        message="; ".join(parts) if parts else "All required fields present",
        details={"missing": missing, "empty": empty},
    )


def check_text_not_empty(
    text: str,
    *,
    min_length: int = 1,
) -> CheckResult:
    """Check that a text field is non-empty and meets a min length."""
    if not isinstance(text, str):
        return CheckResult(
            name="text_not_empty",
            passed=False,
            message=f"Expected str, got {type(text).__name__}",
            severity="error",
        )
    stripped = text.strip()
    if len(stripped) < min_length:
        return CheckResult(
            name="text_not_empty",
            passed=False,
            message=f"Text shorter than {min_length} chars (got {len(stripped)}).",
            severity="warning",
            details={"length": len(stripped)},
        )
    return CheckResult(
        name="text_not_empty",
        passed=True,
        message=f"Text length {len(stripped)} OK.",
        severity="info",
    )


def check_no_placeholders(data: dict[str, Any]) -> CheckResult:
    """
    Detect leftover template placeholders like ${var}, {var}, TODO, FIXME.
    """
    patterns = [
        re.compile(r"\$\{[^}]+\}"),
        re.compile(r"\{\{[^}]+\}\}"),
        re.compile(r"\bTODO\b", re.IGNORECASE),
        re.compile(r"\bFIXME\b", re.IGNORECASE),
        re.compile(r"\bXXX\b"),
    ]

    found: list[str] = []
    for text in _iter_strings(data):
        for pattern in patterns:
            if pattern.search(text):
                found.append(text[:80])

    return CheckResult(
        name="no_placeholders",
        passed=len(found) == 0,
        message=("No placeholders found." if not found else f"Found {len(found)} placeholder(s)."),
        severity="error" if found else "info",
        details={"matches": found},
    )


def check_confidence(
    confidence: float | None,
    *,
    min_confidence: float = 0.0,
) -> CheckResult:
    """
    Check that a confidence value is present and above a threshold.

    confidence=None is treated as "not reported" — a warning, not an error.
    """
    if confidence is None:
        return CheckResult(
            name="confidence",
            passed=True,  # not required
            message="Confidence not reported.",
            severity="warning",
        )
    if not isinstance(confidence, (int, float)) or isinstance(confidence, bool):
        return CheckResult(
            name="confidence",
            passed=False,
            message=f"Confidence must be a number, got {type(confidence).__name__}.",
            severity="error",
        )
    if not 0.0 <= confidence <= 1.0:
        return CheckResult(
            name="confidence",
            passed=False,
            message=f"Confidence {confidence} is outside [0.0, 1.0].",
            severity="error",
        )
    if confidence < min_confidence:
        return CheckResult(
            name="confidence",
            passed=False,
            message=(f"Confidence {confidence} is below required minimum " f"{min_confidence}."),
            severity="warning",
            details={"confidence": confidence, "min": min_confidence},
        )
    return CheckResult(
        name="confidence",
        passed=True,
        message=f"Confidence {confidence} OK.",
        severity="info",
    )


# ============================================================
# PII check
# ============================================================

_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_PHONE_RE = re.compile(r"\b(?:\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b")
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_CREDIT_CARD_RE = re.compile(r"\b(?:\d[ -]?){13,19}\b")


def check_no_pii(
    data: dict[str, Any],
    *,
    allow_emails: bool = False,
    allow_phones: bool = False,
) -> CheckResult:
    """
    Detect obvious PII patterns (emails, phones, SSNs, credit cards).

    If allow_emails=True (e.g. resumes), emails are ignored.
    """
    hits: list[dict[str, str]] = []
    for text in _iter_strings(data):
        if not allow_emails and _EMAIL_RE.search(text):
            hits.append({"type": "email", "sample": text[:60]})
        if not allow_phones and _PHONE_RE.search(text):
            hits.append({"type": "phone", "sample": text[:60]})
        if _SSN_RE.search(text):
            hits.append({"type": "ssn", "sample": text[:60]})
        if _CREDIT_CARD_RE.search(text) and len(re.sub(r"\D", "", text)) >= 13:
            hits.append({"type": "credit_card", "sample": text[:60]})

    return CheckResult(
        name="no_pii",
        passed=len(hits) == 0,
        message=(
            "No PII detected." if not hits else f"Detected {len(hits)} potential PII item(s)."
        ),
        severity="warning" if hits else "info",
        details={"hits": hits},
    )


# ============================================================
# Utilities
# ============================================================


def _iter_strings(data: Any):
    """Recursively yield all string values in a nested structure."""
    if isinstance(data, str):
        yield data
    elif isinstance(data, dict):
        for v in data.values():
            yield from _iter_strings(v)
    elif isinstance(data, (list, tuple, set)):
        for v in data:
            yield from _iter_strings(v)

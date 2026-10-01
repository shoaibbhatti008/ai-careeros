"""Verification module for agent outputs.

The verification layer is the last line of defense against:
- Hallucinations (claims without evidence)
- Schema violations
- Inconsistent outputs
- Overconfidence
- PII leakage

Verification does NOT call an LLM. It uses deterministic checks
that operate on the structured output.
"""

from agents.verification.checks import (
    CheckResult,
    check_confidence,
    check_no_pii,
    check_no_placeholders,
    check_required_fields,
    check_schema,
    check_text_not_empty,
)
from agents.verification.verifier import VerificationReport, Verifier

__all__ = [
    "CheckResult",
    "VerificationReport",
    "Verifier",
    "check_confidence",
    "check_no_pii",
    "check_no_placeholders",
    "check_required_fields",
    "check_schema",
    "check_text_not_empty",
]

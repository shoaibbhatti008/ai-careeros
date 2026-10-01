"""
Verifier: runs a set of checks against agent output.

The verifier is called AFTER an agent returns a result. It produces
a VerificationReport that the caller can act on (accept, warn, reject).

Design:
- Deterministic checks only (no LLM).
- Failed checks do NOT modify the agent output — they are advisory.
- The caller decides the policy (fail-closed vs fail-open).
"""

from dataclasses import dataclass, field
from typing import Any

from agents.verification.checks import (
    CheckResult,
    check_confidence,
    check_no_pii,
    check_no_placeholders,
    check_required_fields,
    check_schema,
)


@dataclass
class VerificationReport:
    """Aggregated verification report."""

    passed: bool
    checks: list[CheckResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def total_checks(self) -> int:
        return len(self.checks)

    @property
    def failed_checks(self) -> list[CheckResult]:
        return [c for c in self.checks if not c.passed]

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0

    def summary(self) -> str:
        if self.passed and not self.warnings:
            return f"All {self.total_checks} checks passed."
        if self.passed and self.warnings:
            return (
                f"Passed with {len(self.warnings)} warning(s) "
                f"out of {self.total_checks} checks."
            )
        return (
            f"Failed: {len(self.errors)} error(s), "
            f"{len(self.warnings)} warning(s) out of {self.total_checks} checks."
        )


class Verifier:
    """
    Verification pipeline.

    Usage:
        v = Verifier(required_fields=["skills", "score"])
        report = v.verify(output, schema=AGENT_SCHEMA)
    """

    def __init__(
        self,
        *,
        required_fields: list[str] | None = None,
        schema: dict[str, Any] | None = None,
        min_confidence: float | None = None,
        allow_pii: bool = False,
        allow_emails: bool = True,  # resumes commonly contain emails
        check_placeholders: bool = True,
    ) -> None:
        self.required_fields = required_fields or []
        self.schema = schema
        self.min_confidence = min_confidence
        self.allow_pii = allow_pii
        self.allow_emails = allow_emails
        self.check_placeholders = check_placeholders

    def verify(
        self,
        data: dict[str, Any],
        *,
        confidence: float | None = None,
    ) -> VerificationReport:
        """Run all configured checks."""
        results: list[CheckResult] = []

        if self.schema:
            results.append(check_schema(data, self.schema))

        if self.required_fields:
            results.append(check_required_fields(data, self.required_fields))

        if self.check_placeholders:
            results.append(check_no_placeholders(data))

        if self.min_confidence is not None:
            results.append(check_confidence(confidence, min_confidence=self.min_confidence))

        if not self.allow_pii:
            results.append(check_no_pii(data, allow_emails=self.allow_emails))

        errors: list[str] = []
        warnings: list[str] = []
        for r in results:
            if r.passed:
                if r.severity == "warning" and r.message:
                    warnings.append(f"[{r.name}] {r.message}")
                continue
            if r.severity == "error":
                errors.append(f"[{r.name}] {r.message}")
            else:
                warnings.append(f"[{r.name}] {r.message}")

        passed = len(errors) == 0
        return VerificationReport(
            passed=passed,
            checks=results,
            warnings=warnings,
            errors=errors,
        )

"""
Output validation for agent results.

Agents produce structured output. This module validates that output
against a simple schema (types only, no full JSON Schema).

Usage:
    validator = OutputValidator(schema)
    result = validator.validate(data)
    if not result.is_valid:
        # handle errors
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ValidationResult:
    """Result of validation."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)


class OutputValidator:
    """
    Minimal schema validator.

    Supported schema keys:
        type:     "object" | "array" | "string" | "integer" | "number" | "boolean"
        properties: dict of field -> schema (for object)
        required: list of required field names (for object)
        items:    schema for array items (for array)
    """

    def __init__(self, schema: dict[str, Any]) -> None:
        self.schema = schema

    def validate(self, data: Any) -> ValidationResult:
        errors: list[str] = []
        self._validate(data, self.schema, errors, path="")
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    def _validate(
        self,
        data: Any,
        schema: dict[str, Any],
        errors: list[str],
        path: str,
    ) -> None:
        expected_type = schema.get("type")
        if expected_type is None:
            return  # no type constraint

        if not self._check_type(data, expected_type):
            errors.append(f"{path or 'root'}: expected {expected_type}, got {type(data).__name__}")
            return

        if expected_type == "object":
            required = schema.get("required", [])
            for field_name in required:
                if field_name not in data:
                    errors.append(f"{path or 'root'}: missing required field '{field_name}'")

            properties = schema.get("properties", {})
            for field_name, field_schema in properties.items():
                if field_name in data:
                    self._validate(
                        data[field_name],
                        field_schema,
                        errors,
                        path=f"{path}.{field_name}" if path else field_name,
                    )

        elif expected_type == "array":
            item_schema = schema.get("items")
            if item_schema:
                for i, item in enumerate(data):
                    self._validate(item, item_schema, errors, path=f"{path}[{i}]")

    @staticmethod
    def _check_type(value: Any, expected: str) -> bool:
        if expected == "object":
            return isinstance(value, dict)
        if expected == "array":
            return isinstance(value, list)
        if expected == "string":
            return isinstance(value, str)
        if expected == "integer":
            return isinstance(value, int) and not isinstance(value, bool)
        if expected == "number":
            return isinstance(value, int | float) and not isinstance(value, bool)
        if expected == "boolean":
            return isinstance(value, bool)
        if expected == "null":
            return value is None
        return True

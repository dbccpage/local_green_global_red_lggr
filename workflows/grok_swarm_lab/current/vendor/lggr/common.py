"""Strict, dependency-free validation and deterministic JSON receipts.

Hashes bind supplied data. They do not establish truth or grant authority.
"""
from __future__ import annotations

from dataclasses import asdict, is_dataclass
from enum import Enum
from fractions import Fraction
import hashlib
import json
from typing import Any, Mapping


class ValidationError(ValueError):
    """Malformed input, as distinct from a valid negative finding."""


def json_value(value: Any) -> Any:
    """Convert exact values to JSON; reject floats and ambiguous object keys."""
    if isinstance(value, Enum):
        return json_value(value.value)
    if is_dataclass(value) and not isinstance(value, type):
        return json_value(asdict(value))
    if isinstance(value, Fraction):
        return str(value)
    if value is None or type(value) in (bool, int, str):
        return value
    if isinstance(value, (list, tuple)):
        return [json_value(item) for item in value]
    if isinstance(value, Mapping):
        if any(type(key) is not str for key in value):
            raise ValidationError("JSON object keys must be strings")
        return {key: json_value(item) for key, item in value.items()}
    raise ValidationError(f"Unsupported value type {type(value).__name__}; use exact integers or rational strings")


def canonical(value: Any) -> str:
    return json.dumps(json_value(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def exact_int(value: Any, name: str, *, minimum: int | None = None) -> int:
    if type(value) is not int:
        raise ValidationError(f"{name} must be an integer, not {type(value).__name__}")
    if minimum is not None and value < minimum:
        raise ValidationError(f"{name} must be >= {minimum}")
    return value


def text(value: Any, name: str) -> str:
    if type(value) is not str or not value.strip():
        raise ValidationError(f"{name} must be a nonempty string")
    return value


def boolean(value: Any, name: str) -> bool:
    if type(value) is not bool:
        raise ValidationError(f"{name} must be a JSON/Python Boolean")
    return value


def fields(data: Any, required: set[str], optional: set[str] | None = None) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValidationError("Expected a JSON object")
    if any(type(k) is not str for k in data):
        raise ValidationError("Object keys must be strings")
    missing = required - data.keys()
    extra = data.keys() - required - (optional or set())
    if missing or extra:
        raise ValidationError(f"Invalid fields: missing={sorted(missing)}, unknown={sorted(extra)}")
    return data


def sequence(value: Any, name: str) -> list | tuple:
    if not isinstance(value, (list, tuple)):
        raise ValidationError(f"{name} must be an array")
    return value


def loads_strict(raw: str) -> Any:
    """Reject duplicate keys and non-finite numbers instead of silently normalizing them."""
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValidationError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def reject_constant(value: str) -> None:
        raise ValidationError(f"Non-finite JSON number: {value}")

    try:
        result = json.loads(raw, object_pairs_hook=pairs, parse_constant=reject_constant)
    except (ValueError, RecursionError) as exc:
        raise ValidationError(f"Invalid JSON: {exc}") from exc
    json_value(result)  # Also rejects finite floats; use rational strings.
    return result

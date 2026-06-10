"""Assertion helpers for REST API responses.

All helpers raise AssertionError with messages carrying enough context to
diagnose the failure from the test report alone.
"""

from typing import Any

import httpx
from jsonschema import Draft202012Validator


def _payload(response: httpx.Response) -> Any:
    """Decode the JSON body, failing with context when it is not JSON."""
    try:
        return response.json()
    except ValueError as error:
        raise AssertionError(
            f"response body is not JSON: {response.text[:200]}"
        ) from error


def assert_status(response: httpx.Response, expected: int) -> None:
    """Assert the status code; the failure message includes the body."""
    if response.status_code != expected:
        raise AssertionError(
            f"expected HTTP {expected}, got {response.status_code}: "
            f"{response.text[:500]}"
        )


def assert_json(response: httpx.Response, expected: Any) -> None:
    """Assert the full JSON payload equals the expected value."""
    actual = _payload(response)
    if actual != expected:
        raise AssertionError(f"expected payload {expected!r}, got {actual!r}")


def assert_json_contains(response: httpx.Response, expected: dict[str, Any]) -> None:
    """Assert the JSON object contains every expected key-value pair."""
    actual = _payload(response)
    if not isinstance(actual, dict):
        raise AssertionError(f"expected a JSON object, got {actual!r}")
    mismatched = {
        key: actual.get(key)
        for key, value in expected.items()
        if actual.get(key) != value
    }
    if mismatched:
        raise AssertionError(
            f"payload mismatch for {sorted(mismatched)}: "
            f"expected {expected!r}, got {mismatched!r}"
        )


def assert_matches_schema(response: httpx.Response, schema: dict[str, Any]) -> None:
    """Assert the JSON payload validates against a JSON Schema (2020-12).

    Reports every violation, not just the first.
    """
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    errors = sorted(
        validator.iter_errors(_payload(response)), key=lambda e: list(e.path)
    )
    if errors:
        details = "; ".join(
            f"{'/'.join(str(part) for part in error.path) or '<root>'}: {error.message}"
            for error in errors
        )
        raise AssertionError(f"schema validation failed: {details}")

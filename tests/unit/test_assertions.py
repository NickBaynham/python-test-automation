"""Unit tests for the API response assertion helpers."""

import httpx
import pytest
from jsonschema.exceptions import SchemaError

from testplatform.assertions import (
    assert_json,
    assert_json_contains,
    assert_matches_schema,
    assert_status,
)


def response(status_code: int = 200, json: object = None) -> httpx.Response:
    return httpx.Response(status_code, json=json)


def test_assert_status_passes_on_match() -> None:
    assert_status(response(204), 204)


def test_assert_status_failure_includes_code_and_body() -> None:
    with pytest.raises(AssertionError, match=r"expected HTTP 200, got 404.*missing"):
        assert_status(response(404, json={"error": "missing"}), 200)


def test_assert_json_passes_on_equal_payload() -> None:
    assert_json(response(json={"id": 1, "name": "Ada"}), {"id": 1, "name": "Ada"})


def test_assert_json_failure_shows_both_payloads() -> None:
    with pytest.raises(AssertionError, match=r"expected.*'id': 2.*got.*'id': 1"):
        assert_json(response(json={"id": 1}), {"id": 2})


def test_assert_json_contains_passes_on_subset() -> None:
    assert_json_contains(response(json={"id": 1, "name": "Ada"}), {"name": "Ada"})


def test_assert_json_contains_failure_names_mismatched_keys() -> None:
    with pytest.raises(AssertionError, match=r"name"):
        assert_json_contains(response(json={"id": 1, "name": "Ada"}), {"name": "Bob"})


def test_assert_json_contains_rejects_non_object_payload() -> None:
    with pytest.raises(AssertionError, match=r"JSON object"):
        assert_json_contains(response(json=[1, 2, 3]), {"id": 1})


USER_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string", "minLength": 1},
    },
    "required": ["id", "name"],
}


def test_assert_matches_schema_passes_on_valid_payload() -> None:
    assert_matches_schema(response(json={"id": 1, "name": "Ada"}), USER_SCHEMA)


def test_assert_matches_schema_reports_all_violations() -> None:
    with pytest.raises(AssertionError) as failure:
        assert_matches_schema(response(json={"id": "x", "name": ""}), USER_SCHEMA)
    message = str(failure.value)
    assert "id" in message
    assert "name" in message


def test_assert_matches_schema_names_the_failing_path() -> None:
    with pytest.raises(AssertionError, match=r"name"):
        assert_matches_schema(response(json={"id": 1, "name": ""}), USER_SCHEMA)


def test_non_json_body_fails_with_context() -> None:
    page = httpx.Response(200, text="<html>service unavailable</html>")
    with pytest.raises(AssertionError, match=r"not JSON.*service unavailable"):
        assert_json(page, {})


def test_invalid_schema_is_rejected_loudly() -> None:
    with pytest.raises(SchemaError):
        assert_matches_schema(response(json={}), {"type": "nonsense"})

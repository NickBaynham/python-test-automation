"""Unit tests for the database state assertion helpers."""

from typing import cast

import pytest

from testplatform.assertions import (
    assert_collection_count,
    assert_document_absent,
    assert_document_exists,
    assert_field_values,
)
from testplatform.db import MongoTarget
from tests.unit.fakes import FakeTarget


@pytest.fixture
def target() -> FakeTarget:
    fake = FakeTarget()
    fake.collection("items").insert_many(
        [
            {"_id": 1, "name": "alpha", "done": False},
            {"_id": 2, "name": "beta", "done": True},
        ]
    )
    return fake


def db(target: FakeTarget) -> MongoTarget:
    return cast(MongoTarget, target)


def test_document_exists_returns_the_document(target: FakeTarget) -> None:
    document = assert_document_exists(db(target), "items", {"name": "alpha"})
    assert document["_id"] == 1


def test_document_exists_fails_with_query_in_message(target: FakeTarget) -> None:
    with pytest.raises(AssertionError, match=r"items.*'name': 'missing'"):
        assert_document_exists(db(target), "items", {"name": "missing"})


def test_document_absent_passes_when_no_match(target: FakeTarget) -> None:
    assert_document_absent(db(target), "items", {"name": "missing"})


def test_document_absent_fails_with_found_document(target: FakeTarget) -> None:
    with pytest.raises(AssertionError, match=r"expected no document.*alpha"):
        assert_document_absent(db(target), "items", {"name": "alpha"})


def test_field_values_passes_on_match(target: FakeTarget) -> None:
    assert_field_values(db(target), "items", {"_id": 2}, {"name": "beta", "done": True})


def test_field_values_fails_naming_mismatched_fields(target: FakeTarget) -> None:
    with pytest.raises(AssertionError, match=r"done.*expected.*False.*got.*True"):
        assert_field_values(db(target), "items", {"_id": 2}, {"done": False})


def test_collection_count_with_and_without_query(target: FakeTarget) -> None:
    assert_collection_count(db(target), "items", 2)
    assert_collection_count(db(target), "items", 1, {"done": True})


def test_collection_count_failure_shows_both_counts(target: FakeTarget) -> None:
    with pytest.raises(AssertionError, match=r"expected 5.*got 2"):
        assert_collection_count(db(target), "items", 5)

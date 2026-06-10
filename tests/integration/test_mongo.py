"""Integration tests for the database layer against dockerized MongoDB."""

from uuid import uuid4

import pytest

from testplatform.assertions import (
    assert_collection_count,
    assert_document_absent,
    assert_document_exists,
    assert_field_values,
)
from testplatform.db import MongoSeeder, MongoTarget

COLLECTION = "platform_integration"


def marker() -> str:
    return f"run-{uuid4().hex[:12]}"


def test_ping_against_live_server(mongo_target: MongoTarget) -> None:
    assert mongo_target.ping() is True


def test_seeded_document_exists(mongo_target: MongoTarget, seeder: MongoSeeder) -> None:
    tag = marker()
    seeder.seed(COLLECTION, {"tag": tag, "name": "alpha"})
    document = assert_document_exists(mongo_target, COLLECTION, {"tag": tag})
    assert document["name"] == "alpha"


def test_field_values_on_seeded_document(
    mongo_target: MongoTarget, seeder: MongoSeeder
) -> None:
    tag = marker()
    seeder.seed(COLLECTION, {"tag": tag, "name": "beta", "count": 3})
    assert_field_values(
        mongo_target, COLLECTION, {"tag": tag}, {"name": "beta", "count": 3}
    )


def test_collection_count_scoped_to_seeded_documents(
    mongo_target: MongoTarget, seeder: MongoSeeder
) -> None:
    tag = marker()
    seeder.seed(COLLECTION, {"tag": tag, "n": 1}, {"tag": tag, "n": 2})
    assert_collection_count(mongo_target, COLLECTION, 2, {"tag": tag})


def test_cleanup_removes_seeded_documents(mongo_target: MongoTarget) -> None:
    tag = marker()
    with MongoSeeder(mongo_target) as seeder:
        seeder.seed(COLLECTION, {"tag": tag})
        assert_document_exists(mongo_target, COLLECTION, {"tag": tag})
    assert_document_absent(mongo_target, COLLECTION, {"tag": tag})


def test_assertion_failures_report_live_state(
    mongo_target: MongoTarget, seeder: MongoSeeder
) -> None:
    tag = marker()
    seeder.seed(COLLECTION, {"tag": tag, "name": "gamma"})
    with pytest.raises(AssertionError, match="expected no document"):
        assert_document_absent(mongo_target, COLLECTION, {"tag": tag})
    with pytest.raises(AssertionError, match="field mismatch"):
        assert_field_values(mongo_target, COLLECTION, {"tag": tag}, {"name": "delta"})

"""Unit tests for the MongoDB client layer (no server required)."""

import pytest
from pymongo.errors import InvalidOperation

from testplatform.config import load_settings
from testplatform.db import MongoTarget


def make_target() -> MongoTarget:
    return MongoTarget("mongodb://localhost:27100", "sampledb")


def test_collection_is_bound_to_the_configured_database() -> None:
    with make_target() as target:
        collection = target.collection("items")
    assert collection.name == "items"
    assert collection.database.name == "sampledb"


def test_database_property_names_the_configured_database() -> None:
    with make_target() as target:
        assert target.database.name == "sampledb"


def test_context_exit_closes_the_client() -> None:
    target = make_target()
    with target:
        target.collection("items")
    with pytest.raises(InvalidOperation):
        target.collection("items").insert_one({"x": 1})


def test_from_settings_uses_configured_url_and_database() -> None:
    with MongoTarget.from_settings(load_settings()) as target:
        assert target.database.name == "sampledb"


def test_ping_is_false_when_server_unreachable() -> None:
    with MongoTarget("mongodb://127.0.0.1:1", "sampledb", timeout_ms=100) as target:
        assert target.ping() is False

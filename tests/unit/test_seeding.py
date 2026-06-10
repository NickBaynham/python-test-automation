"""Unit tests for MongoDB seeding and teardown (no server required)."""

from typing import cast

import pytest

from testplatform.db import MongoSeeder, MongoTarget
from tests.unit.fakes import FakeTarget


@pytest.fixture
def target() -> FakeTarget:
    return FakeTarget()


def make_seeder(target: FakeTarget) -> MongoSeeder:
    return MongoSeeder(cast(MongoTarget, target))


def test_seed_inserts_documents_and_returns_ids(target: FakeTarget) -> None:
    seeder = make_seeder(target)
    ids = seeder.seed("items", {"name": "a"}, {"name": "b"})
    assert len(ids) == 2
    assert target.collections["items"].documents[ids[0]] == {"name": "a"}


def test_cleanup_removes_only_seeded_documents(target: FakeTarget) -> None:
    target.collections["items"].insert_many([{"_id": "keep", "name": "existing"}])
    seeder = make_seeder(target)
    seeder.seed("items", {"name": "mine"})
    seeder.cleanup()
    assert list(target.collections["items"].documents) == ["keep"]


def test_cleanup_spans_multiple_collections(target: FakeTarget) -> None:
    seeder = make_seeder(target)
    seeder.seed("users", {"name": "u"})
    seeder.seed("orders", {"sku": "o"})
    seeder.cleanup()
    assert not target.collections["users"].documents
    assert not target.collections["orders"].documents


def test_cleanup_resets_tracking_for_reuse(target: FakeTarget) -> None:
    seeder = make_seeder(target)
    first = seeder.seed("items", {"name": "one"})
    seeder.cleanup()
    seeder.seed("items", {"name": "two"})
    seeder.cleanup()
    assert first[0] not in target.collections["items"].documents
    assert not target.collections["items"].documents


def test_context_manager_cleans_up_on_exception(target: FakeTarget) -> None:
    with pytest.raises(RuntimeError), make_seeder(target) as seeder:
        seeder.seed("items", {"name": "doomed"})
        raise RuntimeError("test failure")
    assert not target.collections["items"].documents

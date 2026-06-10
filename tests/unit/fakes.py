"""In-memory stand-ins for the MongoTarget operations the platform uses."""

from collections import defaultdict
from itertools import count
from types import SimpleNamespace
from typing import Any


class FakeCollection:
    """Backs the collection operations used by seeding and assertions."""

    def __init__(self) -> None:
        self.documents: dict[Any, dict[str, Any]] = {}
        self._ids = count(1)

    def insert_many(self, documents: list[dict[str, Any]]) -> SimpleNamespace:
        inserted = []
        for document in documents:
            document_id = document.get("_id", next(self._ids))
            self.documents[document_id] = document
            inserted.append(document_id)
        return SimpleNamespace(inserted_ids=inserted)

    def delete_one(self, query: dict[str, Any]) -> None:
        self.documents.pop(query["_id"], None)

    def _matches(self, document: dict[str, Any], query: dict[str, Any]) -> bool:
        return all(document.get(key) == value for key, value in query.items())

    def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        for document in self.documents.values():
            if self._matches(document, query):
                return document
        return None

    def count_documents(self, query: dict[str, Any]) -> int:
        return sum(
            1 for document in self.documents.values() if self._matches(document, query)
        )


class FakeTarget:
    """Stand-in for MongoTarget exposing named fake collections."""

    def __init__(self) -> None:
        self.collections: defaultdict[str, FakeCollection] = defaultdict(FakeCollection)

    def collection(self, name: str) -> FakeCollection:
        return self.collections[name]

"""MongoDB client layer for database state testing."""

from types import TracebackType
from typing import Any, Self

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError

from testplatform.config import Settings

Document = dict[str, Any]


class MongoTarget:
    """Connection to the MongoDB database under test.

    The underlying client connects lazily; construction never blocks on
    an unreachable server.
    """

    def __init__(self, url: str, database: str, timeout_ms: int = 2000) -> None:
        self._client: MongoClient[Document] = MongoClient(
            url, serverSelectionTimeoutMS=timeout_ms
        )
        self._database = self._client[database]

    @classmethod
    def from_settings(cls, settings: Settings) -> Self:
        """Build the target from platform configuration."""
        return cls(str(settings.mongo_url), settings.mongo_database)

    @property
    def database(self) -> Database[Document]:
        return self._database

    def collection(self, name: str) -> Collection[Document]:
        """The named collection in the database under test."""
        return self._database[name]

    def ping(self) -> bool:
        """Return whether the server answers within the timeout."""
        try:
            self._client.admin.command("ping")
        except PyMongoError:
            return False
        return True

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()


class MongoSeeder:
    """Seeds test data and removes exactly what it seeded.

    Cleanup deletes by recorded id and never drops collections, so seeding
    is safe against databases holding data the test does not own.
    """

    def __init__(self, target: MongoTarget) -> None:
        self._target = target
        self._seeded: list[tuple[str, Any]] = []

    def seed(self, collection: str, *documents: Document) -> list[Any]:
        """Insert documents into the collection; return their ids."""
        result = self._target.collection(collection).insert_many(list(documents))
        self._seeded.extend(
            (collection, document_id) for document_id in result.inserted_ids
        )
        return list(result.inserted_ids)

    def cleanup(self) -> None:
        """Delete every document this seeder inserted."""
        for collection, document_id in self._seeded:
            self._target.collection(collection).delete_one({"_id": document_id})
        self._seeded.clear()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.cleanup()

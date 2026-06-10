"""Fixtures for integration tests against the dockerized sample stack."""

from collections.abc import Generator
from typing import Any
from uuid import uuid4

import httpx
import pytest

from testplatform.api import ApiClient
from testplatform.assertions import assert_status
from testplatform.config import load_settings
from testplatform.db import MongoSeeder, MongoTarget


@pytest.fixture(scope="session")
def api_base_url() -> str:
    return str(load_settings().api_base_url)


@pytest.fixture(scope="session", autouse=True)
def require_api(api_base_url: str) -> None:
    """Fail fast with guidance when the sample API is not running."""
    try:
        httpx.get(f"{api_base_url.rstrip('/')}/health", timeout=2.0)
    except httpx.TransportError:
        pytest.fail(
            f"sample API not reachable at {api_base_url}; "
            "start the stack with make docker-up",
            pytrace=False,
        )


@pytest.fixture(scope="session")
def api(api_base_url: str) -> Generator[ApiClient]:
    with ApiClient(api_base_url) as client:
        yield client


@pytest.fixture(scope="session")
def mongo_target() -> Generator[MongoTarget]:
    """Connection to the database under test; fails fast when it is down."""
    settings = load_settings()
    with MongoTarget.from_settings(settings) as target:
        if not target.ping():
            pytest.fail(
                f"MongoDB not reachable at {settings.mongo_url}; "
                "start the stack with make docker-up",
                pytrace=False,
            )
        yield target


@pytest.fixture
def seeder(mongo_target: MongoTarget) -> Generator[MongoSeeder]:
    """Per-test seeder; removes everything it seeded afterwards."""
    with MongoSeeder(mongo_target) as mongo_seeder:
        yield mongo_seeder


@pytest.fixture
def created_item(api: ApiClient) -> Generator[dict[str, Any]]:
    """An item created for this test and deleted afterwards."""
    response = api.post("/items", json_body={"name": f"item-{uuid4().hex[:8]}"})
    assert_status(response, 201)
    item: dict[str, Any] = response.json()
    yield item
    api.request("DELETE", f"/items/{item['id']}")

"""Fixtures for integration tests against the dockerized sample API."""

from collections.abc import Generator
from typing import Any
from uuid import uuid4

import httpx
import pytest

from testplatform.api import ApiClient
from testplatform.assertions import assert_status
from testplatform.config import load_settings


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


@pytest.fixture
def created_item(api: ApiClient) -> Generator[dict[str, Any]]:
    """An item created for this test and deleted afterwards."""
    response = api.post("/items", json_body={"name": f"item-{uuid4().hex[:8]}"})
    assert_status(response, 201)
    item: dict[str, Any] = response.json()
    yield item
    api.request("DELETE", f"/items/{item['id']}")

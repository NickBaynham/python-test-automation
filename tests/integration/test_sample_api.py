"""Integration tests for the API layer against the dockerized sample API."""

from typing import Any

from testplatform.api import ApiCall, ApiClient
from testplatform.assertions import (
    assert_json,
    assert_json_contains,
    assert_matches_schema,
    assert_status,
)

ITEM_SCHEMA = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string", "minLength": 1},
    },
    "required": ["id", "name"],
}


def test_health_endpoint(api: ApiClient) -> None:
    response = api.get("/health")
    assert_status(response, 200)
    assert_json(response, {"status": "ok"})


def test_created_item_matches_schema(created_item: dict[str, Any]) -> None:
    assert set(created_item) == {"id", "name"}


def test_get_returns_created_item(api: ApiClient, created_item: dict[str, Any]) -> None:
    response = api.get(f"/items/{created_item['id']}")
    assert_status(response, 200)
    assert_json(response, created_item)
    assert_matches_schema(response, ITEM_SCHEMA)


def test_list_contains_created_item(
    api: ApiClient, created_item: dict[str, Any]
) -> None:
    response = api.get("/items")
    assert_status(response, 200)
    assert created_item in response.json()


def test_missing_item_returns_404(api: ApiClient) -> None:
    response = api.get("/items/999999")
    assert_status(response, 404)
    assert_json_contains(response, {"detail": "item not found"})


def test_delete_removes_item(api: ApiClient) -> None:
    created = api.post("/items", json_body={"name": "to-delete"})
    assert_status(created, 201)
    item_id = created.json()["id"]
    assert_status(api.request("DELETE", f"/items/{item_id}"), 204)
    assert_status(api.get(f"/items/{item_id}"), 404)


def test_invalid_payload_rejected(api: ApiClient) -> None:
    response = api.post("/items", json_body={"name": ""})
    assert_status(response, 422)


def test_declarative_call_against_live_api(api: ApiClient) -> None:
    response = api.send(ApiCall(method="GET", path="/health"))
    assert_status(response, 200)
    assert_json_contains(response, {"status": "ok"})

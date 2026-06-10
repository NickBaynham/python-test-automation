"""Unit tests for the REST API client layer."""

import json
from typing import Any

import httpx
import pytest
from pydantic import ValidationError

from testplatform.api import ApiCall, ApiClient


class RecordingTransport(httpx.MockTransport):
    """Mock transport that records every request it serves."""

    def __init__(self, response_json: Any = None, status_code: int = 200) -> None:
        self.requests: list[httpx.Request] = []

        def handler(request: httpx.Request) -> httpx.Response:
            self.requests.append(request)
            return httpx.Response(status_code, json=response_json or {"ok": True})

        super().__init__(handler)


def make_client(transport: httpx.MockTransport, **kwargs: Any) -> ApiClient:
    return ApiClient("http://api.local", transport=transport, **kwargs)


def test_request_joins_base_url_and_path() -> None:
    transport = RecordingTransport()
    with make_client(transport) as client:
        response = client.request("GET", "/users")
    assert response.status_code == 200
    assert str(transport.requests[0].url) == "http://api.local/users"


def test_default_headers_sent_with_every_request() -> None:
    transport = RecordingTransport()
    with make_client(transport, headers={"X-Tenant": "acme"}) as client:
        client.request("GET", "/users")
    assert transport.requests[0].headers["X-Tenant"] == "acme"


def test_bearer_token_sets_authorization_header() -> None:
    transport = RecordingTransport()
    with make_client(transport, bearer_token="s3cret") as client:
        client.request("GET", "/users")
    assert transport.requests[0].headers["Authorization"] == "Bearer s3cret"


def test_per_request_headers_override_defaults() -> None:
    transport = RecordingTransport()
    with make_client(transport, headers={"X-Mode": "default"}) as client:
        client.request("GET", "/users", headers={"X-Mode": "special"})
    assert transport.requests[0].headers["X-Mode"] == "special"


def test_get_and_post_helpers() -> None:
    transport = RecordingTransport()
    with make_client(transport) as client:
        client.get("/users", params={"page": "2"})
        client.post("/users", json_body={"name": "Ada"})
    get_request, post_request = transport.requests
    assert get_request.method == "GET"
    assert str(get_request.url) == "http://api.local/users?page=2"
    assert post_request.method == "POST"
    assert json.loads(post_request.content) == {"name": "Ada"}


def test_send_dispatches_declarative_call() -> None:
    transport = RecordingTransport(response_json={"id": 7})
    call = ApiCall(
        method="POST",
        path="/items",
        params={"dry_run": "true"},
        headers={"X-Req": "1"},
        json_body={"sku": "abc"},
    )
    with make_client(transport) as client:
        response = client.send(call)
    request = transport.requests[0]
    assert response.json() == {"id": 7}
    assert request.method == "POST"
    assert str(request.url) == "http://api.local/items?dry_run=true"
    assert request.headers["X-Req"] == "1"
    assert json.loads(request.content) == {"sku": "abc"}


def test_api_call_rejects_unknown_method() -> None:
    with pytest.raises(ValidationError):
        ApiCall.model_validate({"method": "YEET", "path": "/items"})


def test_client_closes_on_context_exit() -> None:
    transport = RecordingTransport()
    client = make_client(transport)
    with client:
        client.get("/users")
    with pytest.raises(RuntimeError):
        client.get("/users")


def test_close_shuts_down_the_client() -> None:
    client = make_client(RecordingTransport())
    client.close()
    with pytest.raises(RuntimeError):
        client.get("/users")

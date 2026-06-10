"""Typed HTTP client layer for REST API testing."""

from collections.abc import Mapping
from types import TracebackType
from typing import Any, Literal, Self

import httpx
from pydantic import BaseModel

Method = Literal["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]


class ApiCall(BaseModel):
    """A declarative REST call, dispatched by ApiClient.send."""

    method: Method = "GET"
    path: str
    params: dict[str, str] = {}
    headers: dict[str, str] = {}
    json_body: Any = None


class ApiClient:
    """HTTP client bound to a base URL, with default headers and bearer auth.

    A transport can be injected for tests (httpx.MockTransport); production
    use leaves it None.
    """

    def __init__(
        self,
        base_url: str,
        *,
        headers: Mapping[str, str] | None = None,
        bearer_token: str | None = None,
        timeout: float = 10.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        default_headers = dict(headers or {})
        if bearer_token:
            default_headers["Authorization"] = f"Bearer {bearer_token}"
        self._client = httpx.Client(
            base_url=base_url,
            headers=default_headers,
            timeout=timeout,
            transport=transport,
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        json_body: Any = None,
    ) -> httpx.Response:
        """Send one request; per-request headers override the defaults."""
        return self._client.request(
            method, path, params=params, headers=headers, json=json_body
        )

    def get(
        self,
        path: str,
        *,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        return self.request("GET", path, params=params, headers=headers)

    def post(
        self,
        path: str,
        *,
        json_body: Any = None,
        params: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> httpx.Response:
        return self.request(
            "POST", path, params=params, headers=headers, json_body=json_body
        )

    def send(self, call: ApiCall) -> httpx.Response:
        """Dispatch a declarative call."""
        return self.request(
            call.method,
            call.path,
            params=call.params,
            headers=call.headers,
            json_body=call.json_body,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> Self:
        self._client.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self._client.__exit__(exc_type, exc, tb)

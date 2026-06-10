"""The full-stack scenario: UI action, API effect, MongoDB state verification."""

from collections.abc import Callable
from uuid import uuid4

from playwright.sync_api import expect

from testplatform.api import ApiClient
from testplatform.assertions import assert_document_exists, assert_json_contains
from testplatform.config import load_settings
from testplatform.db import MongoTarget
from tests.e2e.pages.sample_app import SampleAppPage


def test_ui_action_reaches_api_and_database(
    sample_app: SampleAppPage,
    api_client: ApiClient,
    track_item: Callable[[str], str],
) -> None:
    name = track_item(f"fullstack-{uuid4().hex[:8]}")

    # UI: a tester-visible action in the browser.
    sample_app.open()
    sample_app.add_item(name)
    expect(sample_app.items().filter(has_text=name)).to_have_count(1)

    # API: the same item is served by the REST layer.
    listing = api_client.get("/items")
    match = next(item for item in listing.json() if item["name"] == name)
    response = api_client.get(f"/items/{match['id']}")
    assert_json_contains(response, {"name": name})

    # Database: the document exists with the expected fields.
    with MongoTarget.from_settings(load_settings()) as mongo:
        document = assert_document_exists(mongo, "items", {"name": name})
        assert str(document["_id"]) == match["id"]

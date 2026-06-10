"""End-to-end tests for the sample React application.

Items persist through the API into MongoDB, so tests use unique names,
assert on filtered locators rather than whole-list equality, and clean up
what they create via the track_item fixture.
"""

from collections.abc import Callable
from uuid import uuid4

from playwright.sync_api import expect

from testplatform.api import ApiClient
from tests.e2e.pages.sample_app import SampleAppPage


def unique_name(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:8]}"


def test_page_loads_with_heading(sample_app: SampleAppPage) -> None:
    sample_app.open()
    expect(sample_app.heading).to_be_visible()


def test_added_item_appears_and_input_clears(
    sample_app: SampleAppPage, track_item: Callable[[str], str]
) -> None:
    name = track_item(unique_name("appears"))
    sample_app.open()
    sample_app.add_item(name)
    expect(sample_app.items().filter(has_text=name)).to_have_count(1)
    expect(sample_app.new_item_input).to_have_value("")


def test_items_accumulate_in_order(
    sample_app: SampleAppPage, track_item: Callable[[str], str]
) -> None:
    first = track_item(unique_name("order-a"))
    second = track_item(unique_name("order-b"))
    sample_app.open()
    sample_app.add_item(first)
    sample_app.add_item(second)
    expect(sample_app.items().filter(has_text=first)).to_have_count(1)
    expect(sample_app.items().filter(has_text=second)).to_have_count(1)
    texts = sample_app.items().all_inner_texts()
    assert texts.index(first) < texts.index(second)


def test_blank_input_adds_nothing(
    sample_app: SampleAppPage,
    track_item: Callable[[str], str],
    api_client: ApiClient,
) -> None:
    name = track_item(unique_name("settle"))
    sample_app.open()
    sample_app.add_item("   ")
    sample_app.add_item(name)
    expect(sample_app.items().filter(has_text=name)).to_have_count(1)
    names = [item["name"] for item in api_client.get("/items").json()]
    assert "" not in names
    assert "   " not in names

"""End-to-end tests for the sample React application."""

from playwright.sync_api import expect

from tests.e2e.pages.sample_app import SampleAppPage


def test_page_loads_with_heading(sample_app: SampleAppPage) -> None:
    sample_app.open()
    expect(sample_app.heading).to_be_visible()


def test_added_item_appears_and_input_clears(sample_app: SampleAppPage) -> None:
    sample_app.open()
    sample_app.add_item("Buy milk")
    expect(sample_app.items()).to_have_text(["Buy milk"])
    expect(sample_app.new_item_input).to_have_value("")


def test_items_accumulate_in_order(sample_app: SampleAppPage) -> None:
    sample_app.open()
    sample_app.add_item("first")
    sample_app.add_item("second")
    expect(sample_app.items()).to_have_text(["first", "second"])


def test_blank_input_adds_nothing(sample_app: SampleAppPage) -> None:
    sample_app.open()
    sample_app.add_item("   ")
    sample_app.add_item("real item")
    expect(sample_app.items()).to_have_text(["real item"])

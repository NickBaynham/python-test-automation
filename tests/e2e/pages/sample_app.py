"""Page object for the sample React application."""

from playwright.sync_api import Locator, Page

from testplatform.pages import BasePage


class SampleAppPage(BasePage):
    """The todo-style sample application."""

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.heading = page.get_by_role("heading", name="Sample App")
        self.new_item_input = page.get_by_role("textbox", name="New item")
        self.add_button = page.get_by_role("button", name="Add")
        self.item_list = page.get_by_test_id("item-list")

    @property
    def path(self) -> str:
        return "/"

    @property
    def ready_locator(self) -> Locator:
        return self.heading

    def add_item(self, text: str) -> None:
        """Type an item and submit it."""
        self.new_item_input.fill(text)
        self.add_button.click()

    def items(self) -> Locator:
        """All items currently in the list."""
        return self.item_list.get_by_role("listitem")

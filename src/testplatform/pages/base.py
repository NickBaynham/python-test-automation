"""Base page object for React applications.

Locator conventions for all page objects:

- Prefer role-based locators (page.get_by_role); they follow the
  accessibility tree, which is stable across React re-renders.
- Use test-id locators (page.get_by_test_id) where a role would be
  ambiguous; the application under test exposes data-testid for these.
- Structural CSS and XPath selectors are not allowed.
"""

from abc import ABC, abstractmethod

from playwright.sync_api import Locator, Page


class BasePage(ABC):
    """Common navigation and readiness behavior for all page objects."""

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url.rstrip("/")

    @property
    @abstractmethod
    def path(self) -> str:
        """Path of this page relative to the base URL, starting with '/'."""

    @property
    @abstractmethod
    def ready_locator(self) -> Locator:
        """Locator that is visible exactly when the page is usable."""

    @property
    def url(self) -> str:
        """Full URL of this page."""
        if not self.path.startswith("/"):
            raise ValueError(f"page path must start with '/': {self.path!r}")
        return f"{self.base_url}{self.path}"

    def open(self) -> None:
        """Navigate to this page and wait until it is ready."""
        self.page.goto(self.url)
        self.wait_until_ready()

    def wait_until_ready(self) -> None:
        """Block until the readiness locator is visible, without sleeps."""
        self.ready_locator.wait_for(state="visible")

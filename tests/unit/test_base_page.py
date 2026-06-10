"""Unit tests for the base page object."""

from typing import cast

import pytest
from playwright.sync_api import Locator, Page

from testplatform.pages import BasePage


class FakeLocator:
    """Records readiness waits in place of a Playwright locator."""

    def __init__(self) -> None:
        self.states: list[str] = []

    def wait_for(self, state: str) -> None:
        self.states.append(state)


class FakePage:
    """Records navigations in place of a Playwright page."""

    def __init__(self) -> None:
        self.visited: list[str] = []

    def goto(self, url: str) -> None:
        self.visited.append(url)


class LoginPage(BasePage):
    """Example page object following the platform conventions."""

    def __init__(self, page: Page, base_url: str) -> None:
        super().__init__(page, base_url)
        self.marker = FakeLocator()

    @property
    def path(self) -> str:
        return "/login"

    @property
    def ready_locator(self) -> Locator:
        return cast(Locator, self.marker)


class PathWithoutSlashPage(LoginPage):
    """Misconfigured page whose path violates the leading-slash contract."""

    @property
    def path(self) -> str:
        return "login"


def make_page(base_url: str = "http://app.local") -> LoginPage:
    return LoginPage(cast(Page, FakePage()), base_url)


def test_url_joins_base_and_path() -> None:
    assert make_page().url == "http://app.local/login"


def test_trailing_slash_in_base_url_is_normalized() -> None:
    assert make_page("http://app.local/").url == "http://app.local/login"


def test_path_must_start_with_slash() -> None:
    page = PathWithoutSlashPage(cast(Page, FakePage()), "http://app.local")
    with pytest.raises(ValueError, match="must start with '/'"):
        _ = page.url


def test_open_navigates_then_waits_until_ready() -> None:
    page = make_page()
    page.open()
    fake = cast(FakePage, page.page)
    assert fake.visited == ["http://app.local/login"]
    assert page.marker.states == ["visible"]


def test_base_page_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        BasePage(cast(Page, FakePage()), "http://app.local")  # type: ignore[abstract]

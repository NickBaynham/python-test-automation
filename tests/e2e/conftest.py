"""Fixtures driving e2e tests across the browsers available on this host.

The browser matrix comes from config/browsers.json (written by
`make install-browsers`) and covers Playwright engines and system browser
channels (Chrome, Edge). Failing tests leave a screenshot and a Playwright
trace under test-artifacts/. Paths are anchored to the project root so the
suite behaves the same from any working directory.
"""

import re
from collections.abc import Generator
from contextlib import suppress
from pathlib import Path
from typing import Any, cast

import pytest
from playwright.sync_api import Browser, Error, Page, Playwright, sync_playwright
from pydantic import ValidationError

from testplatform.browsers import CHANNELS, PLAYWRIGHT_ENGINES, load_inventory
from testplatform.config import load_settings
from tests.e2e.pages.sample_app import SampleAppPage

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INVENTORY_FILE = PROJECT_ROOT / "config" / "browsers.json"
ARTIFACTS_DIR = PROJECT_ROOT / "test-artifacts"

phase_report_key = pytest.StashKey[dict[str, pytest.TestReport]]()


def _browser_params() -> list[Any]:
    """Browsers marked available in the inventory: engines and channels."""
    try:
        available = load_inventory(INVENTORY_FILE).browsers
    except OSError, ValidationError:
        available = {}
    names = [
        name
        for name in (*PLAYWRIGHT_ENGINES, *CHANNELS)
        if name in available and available[name].available
    ]
    if names:
        return list(names)
    skip = pytest.mark.skip(
        reason="no usable browser inventory; run make install-browsers first"
    )
    return [pytest.param("chromium", marks=skip)]


@pytest.hookimpl(wrapper=True, tryfirst=True)
def pytest_runtest_makereport(
    item: pytest.Item, call: pytest.CallInfo[None]
) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    """Stash phase reports so fixtures can see whether the test failed."""
    report = yield
    item.stash.setdefault(phase_report_key, {})[report.when or ""] = report
    return report


@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright]:
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(params=_browser_params(), scope="session")
def browser(
    playwright_instance: Playwright, request: pytest.FixtureRequest
) -> Generator[Browser]:
    name = cast(str, request.param)
    engine = CHANNELS[name].engine if name in CHANNELS else name
    launcher = getattr(playwright_instance, engine)
    browser = cast(
        Browser,
        launcher.launch(channel=name) if name in CHANNELS else launcher.launch(),
    )
    yield browser
    browser.close()


@pytest.fixture
def page(browser: Browser, request: pytest.FixtureRequest) -> Generator[Page]:
    context = browser.new_context()
    context.tracing.start(screenshots=True, snapshots=True)
    page = context.new_page()
    yield page
    try:
        reports = request.node.stash.get(phase_report_key, {})
        if any(report.failed for report in reports.values()):
            ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
            stem = re.sub(r"[^\w.-]", "-", request.node.nodeid)
            # The page may already be gone when the failure was a crash;
            # the trace is still worth saving.
            with suppress(Error):
                page.screenshot(path=ARTIFACTS_DIR / f"{stem}.png", full_page=True)
            context.tracing.stop(path=ARTIFACTS_DIR / f"{stem}-trace.zip")
        else:
            context.tracing.stop()
    finally:
        context.close()


@pytest.fixture(scope="session")
def ui_base_url() -> str:
    return str(load_settings().ui_base_url)


@pytest.fixture
def sample_app(page: Page, ui_base_url: str) -> SampleAppPage:
    return SampleAppPage(page, ui_base_url)

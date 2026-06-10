"""Browser detection, installation, and the host availability inventory."""

import shutil
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

from pydantic import BaseModel

INVENTORY_PATH = Path("config/browsers.json")

PLAYWRIGHT_ENGINES = ("chromium", "firefox", "webkit")


class Channel(NamedTuple):
    """A branded system browser Playwright can drive via an engine channel."""

    engine: str
    commands: tuple[str, ...]
    app_paths: tuple[Path, ...]


CHANNELS: dict[str, Channel] = {
    "chrome": Channel(
        engine="chromium",
        commands=("google-chrome", "google-chrome-stable", "chrome"),
        app_paths=(
            Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
            Path("/opt/google/chrome/chrome"),
            Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
            Path("C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"),
        ),
    ),
    "msedge": Channel(
        engine="chromium",
        commands=("microsoft-edge", "microsoft-edge-stable", "msedge"),
        app_paths=(
            Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
            Path("/opt/microsoft/msedge/msedge"),
            Path("C:/Program Files/Microsoft/Edge/Application/msedge.exe"),
            Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
        ),
    ),
}


class BrowserStatus(BaseModel):
    """Availability of one browser on this host."""

    available: bool


class BrowserInventory(BaseModel):
    """Availability of every known browser, persisted as config/browsers.json."""

    browsers: dict[str, BrowserStatus]


def channel_available(channel: str) -> bool:
    """Return whether a system browser channel is installed on this host."""
    spec = CHANNELS[channel]
    found_on_path = any(shutil.which(command) for command in spec.commands)
    return found_on_path or any(path.exists() for path in spec.app_paths)


def install_engine(engine: str) -> bool:
    """Install one Playwright engine; return whether it is available."""
    command = [sys.executable, "-m", "playwright", "install", engine]
    return subprocess.run(command, check=False).returncode == 0  # noqa: S603


def build_inventory() -> BrowserInventory:
    """Install available engines, detect channels, and assemble the inventory."""
    browsers = {
        engine: BrowserStatus(available=install_engine(engine))
        for engine in PLAYWRIGHT_ENGINES
    }
    browsers |= {
        channel: BrowserStatus(available=channel_available(channel))
        for channel in CHANNELS
    }
    return BrowserInventory(browsers=browsers)


def write_inventory(inventory: BrowserInventory, path: Path = INVENTORY_PATH) -> None:
    """Write the inventory to its JSON file, creating parent directories."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(inventory.model_dump_json(indent=2) + "\n")


def load_inventory(path: Path = INVENTORY_PATH) -> BrowserInventory:
    """Load and validate a previously written inventory."""
    return BrowserInventory.model_validate_json(path.read_text())


def main() -> None:
    """Build and persist the browser inventory for this host."""
    inventory = build_inventory()
    write_inventory(inventory)
    for name, status in inventory.browsers.items():
        print(f"{name}: available={str(status.available).lower()}")


if __name__ == "__main__":
    main()

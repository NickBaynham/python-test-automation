"""Unit tests for browser detection and the availability inventory."""

import shutil
import subprocess
from pathlib import Path

import pytest
from pydantic import ValidationError

from testplatform import browsers
from testplatform.browsers import (
    PLAYWRIGHT_ENGINES,
    BrowserInventory,
    BrowserStatus,
    Channel,
    build_inventory,
    channel_available,
    install_engine,
    load_inventory,
    write_inventory,
)


def test_install_engine_available_on_success(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(command: list[str], check: bool) -> subprocess.CompletedProcess[bytes]:
        assert command[-2:] == ["install", "chromium"]
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert install_engine("chromium") is True


def test_install_engine_unavailable_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda command, check: subprocess.CompletedProcess(command, 1),
    )
    assert install_engine("webkit") is False


def test_channel_available_via_path_lookup(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda command: "/usr/bin/fake")
    assert channel_available("chrome") is True


def test_channel_available_via_application_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    app = tmp_path / "chrome.exe"
    app.touch()
    monkeypatch.setattr(shutil, "which", lambda command: None)
    monkeypatch.setattr(
        browsers,
        "CHANNELS",
        {"chrome": Channel(engine="chromium", commands=("chrome",), app_paths=(app,))},
    )
    assert channel_available("chrome") is True


def test_channel_unavailable_when_nothing_found(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(shutil, "which", lambda command: None)
    monkeypatch.setattr(
        browsers,
        "CHANNELS",
        {
            "msedge": Channel(
                engine="chromium",
                commands=("msedge",),
                app_paths=(tmp_path / "missing",),
            )
        },
    )
    assert channel_available("msedge") is False


def test_build_inventory_covers_engines_and_channels(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(browsers, "install_engine", lambda engine: True)
    monkeypatch.setattr(browsers, "channel_available", lambda channel: False)
    inventory = build_inventory()
    for engine in PLAYWRIGHT_ENGINES:
        assert inventory.browsers[engine].available is True
    assert inventory.browsers["chrome"].available is False
    assert inventory.browsers["msedge"].available is False


def test_inventory_round_trip(tmp_path: Path) -> None:
    inventory = BrowserInventory(browsers={"chromium": BrowserStatus(available=True)})
    path = tmp_path / "config" / "browsers.json"
    write_inventory(inventory, path)
    assert load_inventory(path) == inventory


def test_load_inventory_rejects_invalid_content(tmp_path: Path) -> None:
    path = tmp_path / "browsers.json"
    path.write_text('{"browsers": {"chromium": {"available": "maybe"}}}')
    with pytest.raises(ValidationError):
        load_inventory(path)


def test_main_writes_inventory_and_reports(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(browsers, "install_engine", lambda engine: True)
    monkeypatch.setattr(browsers, "channel_available", lambda channel: False)
    browsers.main()
    written = load_inventory(Path("config/browsers.json"))
    assert written.browsers["chromium"].available is True
    out = capsys.readouterr().out
    assert "chromium: available=true" in out
    assert "chrome: available=false" in out

"""Shared fixtures for platform unit tests."""

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolate_working_directory(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Run every unit test in a temporary directory.

    Keeps the repo's .env file out of configuration loading and any file
    output out of the working tree.
    """
    monkeypatch.chdir(tmp_path)

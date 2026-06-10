"""Unit tests for the environment configuration module."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from testplatform.config import TargetMode, load_settings


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """Isolate each test from platform variables and any local .env file."""
    monkeypatch.delenv("TP_ENVIRONMENT", raising=False)
    monkeypatch.delenv("TP_TARGET_MODE", raising=False)
    monkeypatch.chdir(tmp_path)


def test_defaults_to_local_docker() -> None:
    settings = load_settings()
    assert settings.environment == "local"
    assert settings.target_mode is TargetMode.DOCKER


def test_reads_environment_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TP_ENVIRONMENT", "staging")
    monkeypatch.setenv("TP_TARGET_MODE", "remote")
    settings = load_settings()
    assert settings.environment == "staging"
    assert settings.target_mode is TargetMode.REMOTE


def test_rejects_unknown_target_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TP_TARGET_MODE", "mainframe")
    with pytest.raises(ValidationError):
        load_settings()


def test_settings_are_immutable() -> None:
    settings = load_settings()
    with pytest.raises(ValidationError):
        settings.environment = "prod"


def test_rejects_empty_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TP_ENVIRONMENT", "")
    with pytest.raises(ValidationError):
        load_settings()


def test_ignores_unrelated_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TP_FUTURE_OPTION", "anything")
    settings = load_settings()
    assert settings.environment == "local"
    assert settings.target_mode is TargetMode.DOCKER

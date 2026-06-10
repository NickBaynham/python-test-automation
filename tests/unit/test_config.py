"""Unit tests for the environment configuration module."""

import pytest
from pydantic import ValidationError

from testplatform.config import Settings, TargetMode, load_settings


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove platform variables so each test controls its own environment."""
    monkeypatch.delenv("TP_ENVIRONMENT", raising=False)
    monkeypatch.delenv("TP_TARGET_MODE", raising=False)


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


def test_ignores_unrelated_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TP_FUTURE_OPTION", "anything")
    settings = load_settings()
    assert isinstance(settings, Settings)

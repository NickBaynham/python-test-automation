"""Unit tests for the environment configuration module."""

import pytest
from pydantic import ValidationError

from testplatform.config import TargetMode, load_settings


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove platform variables so each test controls its own environment."""
    monkeypatch.delenv("TP_ENVIRONMENT", raising=False)
    monkeypatch.delenv("TP_TARGET_MODE", raising=False)
    monkeypatch.delenv("TP_UI_BASE_URL", raising=False)
    monkeypatch.delenv("TP_API_BASE_URL", raising=False)
    monkeypatch.delenv("TP_MONGO_URL", raising=False)
    monkeypatch.delenv("TP_MONGO_DATABASE", raising=False)


def test_defaults_to_local_docker() -> None:
    settings = load_settings()
    assert settings.environment == "local"
    assert settings.target_mode is TargetMode.DOCKER


def test_reads_environment_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TP_ENVIRONMENT", "staging")
    monkeypatch.setenv("TP_TARGET_MODE", "remote")
    monkeypatch.setenv("TP_UI_BASE_URL", "https://staging.example.com")
    monkeypatch.setenv("TP_API_BASE_URL", "https://api.staging.example.com")
    monkeypatch.setenv("TP_MONGO_URL", "mongodb://db.staging.example.com:27017")
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


def test_ui_base_url_defaults_to_local_sample_app() -> None:
    settings = load_settings()
    assert str(settings.ui_base_url) == "http://localhost:3100/"


def test_ui_base_url_read_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TP_UI_BASE_URL", "https://staging.example.com")
    settings = load_settings()
    assert str(settings.ui_base_url) == "https://staging.example.com/"


def test_rejects_invalid_ui_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TP_UI_BASE_URL", "not-a-url")
    with pytest.raises(ValidationError):
        load_settings()


def test_remote_mode_requires_explicit_ui_base_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TP_TARGET_MODE", "remote")
    with pytest.raises(ValidationError, match="TP_UI_BASE_URL"):
        load_settings()


def test_api_base_url_defaults_to_local_sample_api() -> None:
    settings = load_settings()
    assert str(settings.api_base_url) == "http://localhost:8100/"


def test_api_base_url_read_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TP_API_BASE_URL", "https://api.staging.example.com")
    settings = load_settings()
    assert str(settings.api_base_url) == "https://api.staging.example.com/"


def test_remote_mode_requires_every_target_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TP_TARGET_MODE", "remote")
    monkeypatch.setenv("TP_UI_BASE_URL", "https://app.example.com")
    with pytest.raises(ValidationError, match="TP_API_BASE_URL"):
        load_settings()


def test_remote_mode_with_all_targets_explicit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("TP_TARGET_MODE", "remote")
    monkeypatch.setenv("TP_UI_BASE_URL", "https://app.example.com")
    monkeypatch.setenv("TP_API_BASE_URL", "https://api.example.com")
    monkeypatch.setenv("TP_MONGO_URL", "mongodb://db.example.com:27017")
    settings = load_settings()
    assert str(settings.api_base_url) == "https://api.example.com/"
    assert str(settings.mongo_url).rstrip("/") == "mongodb://db.example.com:27017"


def test_mongo_defaults_to_local_database() -> None:
    settings = load_settings()
    assert str(settings.mongo_url).rstrip("/") == "mongodb://localhost:27100"
    assert settings.mongo_database == "sampledb"


def test_mongo_url_read_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TP_MONGO_URL", "mongodb://db.example.com:27017")
    monkeypatch.setenv("TP_MONGO_DATABASE", "orders")
    settings = load_settings()
    assert str(settings.mongo_url).rstrip("/") == "mongodb://db.example.com:27017"
    assert settings.mongo_database == "orders"


def test_rejects_invalid_mongo_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TP_MONGO_URL", "http://not-a-mongo-url")
    with pytest.raises(ValidationError):
        load_settings()


def test_remote_mode_requires_mongo_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TP_TARGET_MODE", "remote")
    monkeypatch.setenv("TP_UI_BASE_URL", "https://app.example.com")
    monkeypatch.setenv("TP_API_BASE_URL", "https://api.example.com")
    with pytest.raises(ValidationError, match="TP_MONGO_URL"):
        load_settings()


def test_ignores_unrelated_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TP_FUTURE_OPTION", "anything")
    settings = load_settings()
    assert settings.environment == "local"
    assert settings.target_mode is TargetMode.DOCKER

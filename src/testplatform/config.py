"""Environment configuration loaded from TP_-prefixed environment variables."""

from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict


class TargetMode(StrEnum):
    """Where the application under test runs."""

    DOCKER = "docker"
    REMOTE = "remote"


class Settings(BaseSettings):
    """Platform settings for the current run.

    Later phases extend this with UI, API, and database target settings.
    Secrets must always come from environment variables, never from code.
    """

    model_config = SettingsConfigDict(
        env_prefix="TP_",
        env_file=".env",
        extra="ignore",
        frozen=True,
    )

    environment: str = "local"
    target_mode: TargetMode = TargetMode.DOCKER


def load_settings() -> Settings:
    """Load settings from the process environment."""
    return Settings()

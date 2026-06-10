"""Environment configuration loaded from TP_-prefixed environment variables."""

from enum import StrEnum
from typing import Self

from pydantic import Field, HttpUrl, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class TargetMode(StrEnum):
    """Where the application under test runs."""

    DOCKER = "docker"
    REMOTE = "remote"


# Target fields whose localhost defaults must not leak into remote runs.
# Phase 2 (API) and Phase 3 (MongoDB) add their target fields here.
_REMOTE_REQUIRED_FIELDS = ("ui_base_url",)


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

    environment: str = Field(default="local", min_length=1)
    target_mode: TargetMode = TargetMode.DOCKER
    ui_base_url: HttpUrl = HttpUrl("http://localhost:3100")

    @model_validator(mode="after")
    def _require_explicit_urls_for_remote(self) -> Self:
        if self.target_mode is not TargetMode.REMOTE:
            return self
        missing = [
            f"TP_{name.upper()}"
            for name in _REMOTE_REQUIRED_FIELDS
            if name not in self.model_fields_set
        ]
        if missing:
            raise ValueError(
                f"remote target mode requires explicit values for: {', '.join(missing)}"
            )
        return self


def load_settings() -> Settings:
    """Load settings from the process environment."""
    return Settings()

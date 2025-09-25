"""Application configuration primitives."""
from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    openai_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None
    fashion_analyzer_model: str = "gpt-4o-mini"
    sustainability_analyzer_model: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached instance of :class:`Settings`."""

    return Settings()  # type: ignore[call-arg]


__all__ = ["Settings", "get_settings"]

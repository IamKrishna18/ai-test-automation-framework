"""Application configuration loaded from environment variables.

Uses pydantic-settings to parse .env files and environment variables
into a typed Settings object. All configuration access should go
through `get_settings()` to leverage caching.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings sourced from .env and environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---- LLM Provider API Keys ----
    gemini_api_key: str = ""
    openai_api_key: str = ""

    # ---- Default LLM Settings ----
    default_llm_provider: str = "gemini"
    default_llm_model: str = "gemini-2.5-flash"

    # ---- Database ----
    database_url: str = "sqlite:///./data/test_automation.db"

    # ---- Server ----
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    frontend_url: str = "http://localhost:5173"

    # ---- Target API Defaults ----
    default_request_timeout: int = 30
    max_spec_size_mb: int = 5

    # ---- Logging ----
    log_level: str = "INFO"

    # ---- Derived paths ----
    @property
    def reports_dir(self) -> Path:
        """Directory for generated reports."""
        path = Path("reports")
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def data_dir(self) -> Path:
        """Directory for database files."""
        path = Path("data")
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Using lru_cache ensures the .env file is read only once and the
    same Settings object is reused throughout the application.
    """
    return Settings()

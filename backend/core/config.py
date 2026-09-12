"""Pydantic settings for MatchSense configuration.

Loads from environment variables or .env file. All settings have sensible
defaults for local development with Docker Compose.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Database
    database_url: str = "postgresql://matchsense:matchsense@localhost:5432/matchsense"

    # Model
    model_path: str = "data/models/dixon_coles_latest.pkl"

    # Football-Data.org API (Phase 3)
    football_data_api_key: str = ""

    # Logging
    log_level: str = "INFO"

    # API
    api_v1_prefix: str = "/api/v1"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

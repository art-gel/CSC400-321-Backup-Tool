"""Application settings.

Settings come from environment variables (or a .env file) so that secrets like
the API key and AWS credentials never get hard-coded into the source. This is
the single place the whole app reads configuration from.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BACKUP_", env_file=".env", extra="ignore")

    # --- API security ---
    # The tray UI sends this in the "X-API-Key" header on every request.
    # Generate a random one per install; do NOT ship a default in production.
    api_key: str = "dev-local-key-change-me"

    # --- Where the API listens ---
    host: str = "127.0.0.1"  # localhost only — this is a local service, not public
    port: int = 8787

    # --- Default backup destination (can be overridden via PUT /v1/config) ---
    s3_bucket: str = "my-backups-bucket"
    aws_region: str = "us-east-1"

    # --- Retention: how many backups to keep before pruning the oldest ---
    retention_count: int = 5


@lru_cache
def get_settings() -> Settings:
    """Cached so we build the Settings object once per process."""
    return Settings()

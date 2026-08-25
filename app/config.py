from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    helios_env: str = "development"
    helios_log_level: str = "INFO"
    helios_api_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg://helios:helios@localhost:5432/helios"

    fortyguard_api_key: str = Field(default="", repr=False)
    fortyguard_base_url: str = "https://api.fortyguard.com"
    fortyguard_timeout_seconds: float = 30.0
    fortyguard_poll_interval_seconds: float = 2.0
    fortyguard_max_poll_seconds: float = 120.0
    fortyguard_cache_ttl_seconds: int = 900
    fortyguard_max_retries: int = 3

@lru_cache
def get_settings() -> Settings:
    return Settings()

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Development mode (default) or production
    MODE: str = "development"

    # API Configuration
    OPEN_ROUTER_API_KEY: str | None = None
    LLM_MODEL: str = "gpt-4o"

    # Authentication Settings
    GITHUB_TOKEN: str | None = None
    SUPABASE_URL: str | None = None
    SUPABASE_SERVICE_KEY: str | None = None
    API_BEARER_TOKEN: str | None = None


# Cache the settings to avoid reloading the .env file repeatedly
@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


# Initialize settings
settings = get_settings()

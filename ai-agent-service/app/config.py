from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables and/or a .env file.
    """

    # Service settings
    app_name: str = "leave-policy-agent-service"
    environment: str = "development"
    debug: bool = True
    port: int = 8000
    host: str = "0.0.0.0"

    # LLM settings
    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached instance of the settings object.
    """
    return Settings()

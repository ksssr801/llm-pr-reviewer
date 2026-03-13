from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables and/or a .env file.
    """

    # Service settings
    app_name: str = "ai-code-review-agent"
    environment: str = "development"
    debug: bool = True
    port: int = 8000
    host: str = "0.0.0.0"

    # LLM settings
    openai_api_key: str = ""
    llm_model: str = "gpt-4o-mini"
    
    # Github Integration
    github_token: str = ""
    github_webhook_secret: str = ""
    ai_review_label: str = "ai-review"
    github_api_base: str = "https://api.github.com"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        case_sensitive=False, 
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached instance of the settings object. Prevents reload of settings on every request.
    """
    return Settings()

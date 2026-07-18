from functools import lru_cache
from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    app_name: str = (
        "Enterprise AI Workspace"
    )

    app_env: str = "development"
    debug: bool = True

    api_v1_prefix: str = "/api"

    database_url: str

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    jwt_secret_key: str
    jwt_refresh_secret_key: str
    jwt_algorithm: str = "HS256"

    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Sprint 2 LLM settings
    llm_provider: str = Field(
        default="groq",
        validation_alias="LLM_PROVIDER",
    )

    groq_api_key: str | None = Field(
        default=None,
        validation_alias="GROQ_API_KEY",
    )

    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        validation_alias="GROQ_MODEL",
    )

    openai_api_key: str | None = Field(
        default=None,
        validation_alias="OPENAI_API_KEY",
    )

    openai_model: str = Field(
        default="gpt-4o-mini",
        validation_alias="OPENAI_MODEL",
    )

    ollama_base_url: str = Field(
        default="http://localhost:11434",
        validation_alias="OLLAMA_BASE_URL",
    )

    ollama_model: str = Field(
        default="llama3.2",
        validation_alias="OLLAMA_MODEL",
    )

    llm_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        validation_alias="LLM_TEMPERATURE",
    )

    llm_max_tokens: int = Field(
        default=1024,
        ge=1,
        le=32768,
        validation_alias="LLM_MAX_TOKENS",
    )

    llm_timeout_seconds: float = Field(
        default=60.0,
        ge=1.0,
        validation_alias="LLM_TIMEOUT_SECONDS",
    )

    llm_max_retries: int = Field(
        default=3,
        ge=1,
        le=10,
        validation_alias="LLM_MAX_RETRIES",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
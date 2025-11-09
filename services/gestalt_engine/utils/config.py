"""Configuration management for Gestalt Design Engine."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    SERVICE_NAME: str = "gestalt-design-engine"
    SERVICE_VERSION: str = "1.0.0"
    PORT: int = 8002
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = ["*"]

    # AI/LLM configuration (disabled for v1)
    AI_MODE_ENABLED: bool = False
    OPENAI_API_KEY: str | None = None

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

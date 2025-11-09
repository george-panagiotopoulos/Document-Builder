"""Configuration management for User Agent."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    SERVICE_NAME: str = "user-agent"
    SERVICE_VERSION: str = "1.0.0"

    # Downstream service URLs
    CONTENT_INTAKE_URL: str = "http://localhost:8001/v1"
    GESTALT_ENGINE_URL: str = "http://localhost:8002/v1"
    DOCUMENT_FORMATTER_URL: str = "http://localhost:8003/v1"

    # Workflow settings
    MAX_POLL_ATTEMPTS: int = 30
    POLL_INTERVAL_SECONDS: float = 2.0

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = True


settings = Settings()

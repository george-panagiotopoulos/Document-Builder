"""
Configuration management for Content Intake Service.

Loads configuration from environment variables and provides
application-wide settings.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Service configuration
    SERVICE_NAME: str = "content-intake-service"
    SERVICE_VERSION: str = "1.0.0"
    PORT: int = 8001
    LOG_LEVEL: str = "INFO"

    # CORS configuration
    CORS_ORIGINS: list[str] = ["*"]

    # Database configuration - PostgreSQL
    DATABASE_URL: str = "postgresql://docbuilder:changeme@localhost:5432/document_builder"

    # Object storage configuration
    STORAGE_BUCKET: str = "document-builder-assets"

    # Downstream services
    GESTALT_ENGINE_URL: str = "http://localhost:8002/v1"

    # Rate limiting
    MAX_REQUESTS_PER_MINUTE: int = 30

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

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
    LOG_LEVEL: str = "INFO"

    # CORS configuration
    CORS_ORIGINS: list[str] = ["*"]

    # Database configuration - PostgreSQL
    DATABASE_URL: str = "postgresql://docbuilder:changeme@localhost:5432/document_builder"

    # Object storage configuration (placeholder)
    STORAGE_BUCKET: str = "document-builder-assets"

    # Downstream services
    GESTALT_ENGINE_URL: str = "https://gestalt.document-builder.internal/v1"

    # Rate limiting
    MAX_REQUESTS_PER_MINUTE: int = 30

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = True


settings = Settings()

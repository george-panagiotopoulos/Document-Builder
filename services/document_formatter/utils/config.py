"""Configuration management for Document Formatter Service."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    SERVICE_NAME: str = "document-formatter-service"
    SERVICE_VERSION: str = "1.0.0"
    PORT: int = 8003
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: list[str] = ["*"]

    # Storage configuration
    STORAGE_BUCKET: str = "document-builder-artifacts"
    STORAGE_REGION: str = "us-east-1"

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

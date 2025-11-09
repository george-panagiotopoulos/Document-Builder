"""Configuration management for Document Formatter Service."""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings."""

    SERVICE_NAME: str = Field(..., alias="FORMATTER_SERVICE_NAME", description="Service name")
    SERVICE_VERSION: str = Field(..., alias="FORMATTER_SERVICE_VERSION", description="Service version")
    PORT: int = Field(..., alias="DOCUMENT_FORMATTER_PORT", description="Service port")
    LOG_LEVEL: str = Field(..., alias="FORMATTER_LOG_LEVEL", description="Logging level")
    CORS_ORIGINS: str = Field(..., alias="FORMATTER_CORS_ORIGINS", description="Allowed CORS origins (comma-separated)")
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as list (for FastAPI CORS middleware)."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # Storage configuration
    STORAGE_BUCKET: str = Field(..., description="S3-compatible storage bucket")
    STORAGE_REGION: str = Field(..., description="Storage region")

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        populate_by_name = True
        extra = "ignore"  # Ignore extra environment variables not defined in this model


settings = Settings()

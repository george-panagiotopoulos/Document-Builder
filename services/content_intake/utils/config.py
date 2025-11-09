"""
Configuration management for Content Intake Service.

Loads configuration from environment variables and provides
application-wide settings.

IMPORTANT: All configuration MUST come from .env file.
No hardcoded defaults - copy .env.example to .env and configure.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings."""

    # Service configuration
    SERVICE_NAME: str = Field(..., alias="CONTENT_INTAKE_SERVICE_NAME", description="Service name")
    SERVICE_VERSION: str = Field(..., alias="CONTENT_INTAKE_SERVICE_VERSION", description="Service version")
    PORT: int = Field(..., alias="CONTENT_INTAKE_PORT", description="Service port")
    LOG_LEVEL: str = Field(..., alias="CONTENT_INTAKE_LOG_LEVEL", description="Logging level")

    # CORS configuration (comma-separated string in .env)
    CORS_ORIGINS: str = Field(..., alias="CONTENT_INTAKE_CORS_ORIGINS", description="Allowed CORS origins (comma-separated)")

    # Database configuration - PostgreSQL (REQUIRED)
    DATABASE_URL: str = Field(
        ...,
        description="PostgreSQL connection string. Format: postgresql://user:password@host:port/database"
    )

    # Object storage configuration
    STORAGE_BUCKET: str = Field(..., description="S3-compatible storage bucket")

    # Downstream services
    GESTALT_ENGINE_URL: str = Field(..., description="Gestalt Design Engine service URL")
    DOCUMENT_FORMATTER_URL: str = Field(..., description="Document Formatter service URL")

    # Rate limiting
    MAX_REQUESTS_PER_MINUTE: int = Field(..., description="Maximum requests per minute")

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        populate_by_name = True  # Allow both field name and alias
        extra = "ignore"  # Ignore extra environment variables not defined in this model
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as list (for FastAPI CORS middleware)."""
        if isinstance(self.CORS_ORIGINS, list):
            return self.CORS_ORIGINS
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()

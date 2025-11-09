"""
Gestalt Design Engine main application entry point.

This service converts normalized content and intent metadata into detailed layout
specifications that embody Gestalt and information design principles.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.gestalt_engine.api import proposals
from services.gestalt_engine.utils.config import settings
from services.gestalt_engine.utils.logging import setup_logging

# Set up structured logging
setup_logging()

app = FastAPI(
    title="Gestalt Design Engine",
    description="Converts content into layout specifications using Gestalt principles",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(proposals.router, prefix="/v1/layout", tags=["proposals"])


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "gestalt-engine"}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"service": "Gestalt Design Engine", "version": "1.0.0"}

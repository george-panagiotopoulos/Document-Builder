"""
Content Intake Service main application entry point.

This service receives source material, intent metadata, and assets from the user agent.
It validates and normalizes the submission, assembles a Content-Intent Package (CIP),
and coordinates downstream calls to the Gestalt Design Engine.
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from services.content_intake.api import sessions
from services.content_intake.ui import routes as ui_routes
from services.content_intake.utils.config import settings
from services.content_intake.utils.logging import setup_logging

# Set up structured logging
setup_logging()

app = FastAPI(
    title="Content Intake Service",
    description="Receives, validates, and normalizes content for document generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = Path(__file__).parent / "ui" / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include routers
app.include_router(sessions.router, prefix="/v1/intake", tags=["sessions"])
app.include_router(ui_routes.router, tags=["ui"])


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "content-intake"}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"service": "Content Intake Service", "version": "1.0.0"}

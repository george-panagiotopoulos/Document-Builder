"""
Document Formatter Service main application entry point.

This service transforms Layout Specification Packages (LSP) into Microsoft
Word and PowerPoint artifacts using python-docx and python-pptx.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.document_formatter.api import rendering, artifacts
from services.document_formatter.utils.config import settings
from services.document_formatter.utils.logging import setup_logging

setup_logging()

app = FastAPI(
    title="Document Formatter Service",
    description="Transforms LSP into Word and PowerPoint documents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rendering.router, prefix="/v1/render", tags=["rendering"])
app.include_router(artifacts.router, prefix="/v1", tags=["artifacts"])


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "document-formatter"}


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"service": "Document Formatter Service", "version": "1.0.0"}

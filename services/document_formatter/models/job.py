"""Data models for render jobs and artifacts."""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class RenderJobStatus(str, Enum):
    """Render job lifecycle states."""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PENDING_STORAGE = "pending_storage"


class FileType(str, Enum):
    """Output file types."""

    DOCX = "docx"
    PPTX = "pptx"


class RenderRequest(BaseModel):
    """Request to render a document."""

    layout_specification: dict[str, Any]
    callback_url: str | None = None


class RenderJobResponse(BaseModel):
    """Response containing render job details."""

    render_job_id: str
    status: RenderJobStatus
    artifact_id: str | None = None
    error: str | None = None
    warnings: list[str] = Field(default_factory=list)


class ArtifactResponse(BaseModel):
    """Response containing artifact download information."""

    artifact_id: str
    download_url: str
    expires_at: datetime
    file_type: FileType
    size_bytes: int | None = None


class RenderJob(BaseModel):
    """Internal render job model."""

    render_job_id: str = Field(default_factory=lambda: f"job-{uuid4().hex[:8]}")
    status: RenderJobStatus = RenderJobStatus.QUEUED
    layout_specification: dict[str, Any]
    artifact_id: str | None = None
    error: str | None = None
    warnings: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

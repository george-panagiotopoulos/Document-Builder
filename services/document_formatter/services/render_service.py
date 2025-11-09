"""Render service business logic."""

from typing import Any

from services.document_formatter.models.job import RenderJob, RenderJobStatus, FileType
from services.document_formatter.renderers.word_renderer import WordRenderer
from services.document_formatter.renderers.pptx_renderer import PowerPointRenderer


class RenderService:
    """Service for managing render jobs."""

    def __init__(self) -> None:
        """Initialize render service."""
        self._jobs: dict[str, RenderJob] = {}
        self._word_renderer = WordRenderer()
        self._pptx_renderer = PowerPointRenderer()
        # Track artifact IDs for lookup
        self._artifact_to_job: dict[str, str] = {}

    async def render_document(self, lsp: dict[str, Any]) -> RenderJob:
        """Render Word document from LSP."""
        # Validate LSP
        if not self._validate_lsp(lsp):
            raise ValueError("Invalid LSP: missing required fields")

        # Create job
        job = RenderJob(layout_specification=lsp)
        self._jobs[job.render_job_id] = job

        # Render document (synchronous for v1, async job queue in production)
        try:
            job.status = RenderJobStatus.PROCESSING
            artifact_id = await self._word_renderer.render(lsp)
            job.artifact_id = artifact_id
            job.status = RenderJobStatus.COMPLETE
            # Track artifact for lookup
            self._artifact_to_job[artifact_id] = job.render_job_id
        except Exception as e:
            job.status = RenderJobStatus.FAILED
            job.error = str(e)

        return job

    async def render_presentation(self, lsp: dict[str, Any]) -> RenderJob:
        """Render PowerPoint presentation from LSP."""
        # Validate LSP
        if not self._validate_lsp(lsp):
            raise ValueError("Invalid LSP: missing required fields")

        # Create job
        job = RenderJob(layout_specification=lsp)
        self._jobs[job.render_job_id] = job

        # Render presentation
        try:
            job.status = RenderJobStatus.PROCESSING
            artifact_id = await self._pptx_renderer.render(lsp)
            job.artifact_id = artifact_id
            job.status = RenderJobStatus.COMPLETE
            # Track artifact for lookup
            self._artifact_to_job[artifact_id] = job.render_job_id
        except Exception as e:
            job.status = RenderJobStatus.FAILED
            job.error = str(e)

        return job

    async def get_job(self, render_job_id: str) -> RenderJob | None:
        """Retrieve job by ID."""
        return self._jobs.get(render_job_id)

    async def cancel_job(self, render_job_id: str) -> None:
        """Cancel a render job."""
        job = self._jobs.get(render_job_id)
        if job and job.status in [RenderJobStatus.QUEUED, RenderJobStatus.PROCESSING]:
            job.status = RenderJobStatus.CANCELLED

    def _validate_lsp(self, lsp: dict[str, Any]) -> bool:
        """Validate LSP structure."""
        required_fields = ["schema_version", "proposal_id", "session_id", "document_type", "structure"]
        return all(field in lsp for field in required_fields)

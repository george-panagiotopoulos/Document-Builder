"""API endpoints for document rendering."""

from fastapi import APIRouter, HTTPException, status

from services.document_formatter.models.job import RenderJobResponse, RenderRequest
from services.document_formatter.services.render_service import RenderService

router = APIRouter()
render_service = RenderService()


@router.post("/documents", response_model=RenderJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def render_document(request: RenderRequest) -> RenderJobResponse:
    """
    Accept an LSP and initiate Word document generation.

    Returns render_job_id for polling status.
    """
    try:
        job = await render_service.render_document(request.layout_specification)
        return RenderJobResponse(
            render_job_id=job.render_job_id,
            status=job.status,
            artifact_id=job.artifact_id,
            warnings=job.warnings,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/presentations", response_model=RenderJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def render_presentation(request: RenderRequest) -> RenderJobResponse:
    """
    Accept an LSP and initiate PowerPoint generation.

    Returns render_job_id for polling status.
    """
    try:
        job = await render_service.render_presentation(request.layout_specification)
        return RenderJobResponse(
            render_job_id=job.render_job_id,
            status=job.status,
            artifact_id=job.artifact_id,
            warnings=job.warnings,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/jobs/{render_job_id}", response_model=RenderJobResponse)
async def get_render_job(render_job_id: str) -> RenderJobResponse:
    """Retrieve job status and artifact references."""
    job = await render_service.get_job(render_job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    return RenderJobResponse(
        render_job_id=job.render_job_id,
        status=job.status,
        artifact_id=job.artifact_id,
        error=job.error,
        warnings=job.warnings,
    )


@router.post("/jobs/{render_job_id}/cancel")
async def cancel_render_job(render_job_id: str) -> dict[str, str]:
    """Attempt to cancel in-progress rendering."""
    job = await render_service.get_job(render_job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    await render_service.cancel_job(render_job_id)
    return {"status": "cancellation_requested"}

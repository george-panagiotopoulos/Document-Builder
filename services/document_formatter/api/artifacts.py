"""API endpoints for artifact management."""

from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, status

from services.document_formatter.models.job import ArtifactResponse, FileType

router = APIRouter()

# In-memory artifact storage (placeholder for S3 integration)
_artifacts: dict[str, dict[str, any]] = {}


@router.get("/artifacts/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(artifact_id: str) -> ArtifactResponse:
    """
    Download generated files or obtain time-limited access URLs.

    Returns download URL with 24-hour expiration.
    """
    artifact = _artifacts.get(artifact_id)
    if not artifact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found")

    # Generate time-limited download URL (placeholder)
    download_url = f"https://storage.document-builder.internal/artifacts/{artifact_id}"
    expires_at = datetime.utcnow() + timedelta(hours=24)

    return ArtifactResponse(
        artifact_id=artifact_id,
        download_url=download_url,
        expires_at=expires_at,
        file_type=artifact.get("file_type", FileType.DOCX),
        size_bytes=artifact.get("size_bytes"),
    )

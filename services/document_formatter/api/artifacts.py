"""API endpoints for artifact management."""

import logging
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from services.document_formatter.models.job import ArtifactResponse, FileType

logger = logging.getLogger(__name__)

router = APIRouter()

# Artifact storage directory (absolute path from project root)
# Calculate from this file: services/document_formatter/api/artifacts.py
# Go up 4 levels to get to project root
_project_root = Path(__file__).parent.parent.parent.parent.resolve()
ARTIFACTS_DIR = _project_root / "infrastructure" / "data" / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

logger.info(f"Artifacts directory: {ARTIFACTS_DIR} (exists: {ARTIFACTS_DIR.exists()})")


@router.get("/artifacts/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(artifact_id: str) -> ArtifactResponse:
    """
    Get artifact metadata.

    Returns artifact information including download URL.
    """
    # Check both locations (new and old for migration)
    old_artifacts_dir = _project_root / "artifacts"
    docx_file = ARTIFACTS_DIR / f"{artifact_id}.docx"
    pptx_file = ARTIFACTS_DIR / f"{artifact_id}.pptx"
    old_docx_file = old_artifacts_dir / f"{artifact_id}.docx"
    old_pptx_file = old_artifacts_dir / f"{artifact_id}.pptx"
    
    file_path = None
    file_type = None
    
    # Check new location first, then old location
    if docx_file.exists():
        file_path = docx_file
        file_type = FileType.DOCX
    elif old_docx_file.exists():
        file_path = old_docx_file
        file_type = FileType.DOCX
    elif pptx_file.exists():
        file_path = pptx_file
        file_type = FileType.PPTX
    elif old_pptx_file.exists():
        file_path = old_pptx_file
        file_type = FileType.PPTX
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Artifact not found")

    download_url = f"/v1/artifacts/{artifact_id}/download"
    expires_at = datetime.utcnow() + timedelta(hours=24)
    size_bytes = file_path.stat().st_size if file_path else None

    return ArtifactResponse(
        artifact_id=artifact_id,
        download_url=download_url,
        expires_at=expires_at,
        file_type=file_type,
        size_bytes=size_bytes,
    )


@router.get("/artifacts/{artifact_id}/download")
async def download_artifact(artifact_id: str):
    """
    Download generated document file.

    Serves the actual file for download.
    """
    # Check both locations (new and old for migration)
    old_artifacts_dir = _project_root / "artifacts"
    docx_file = ARTIFACTS_DIR / f"{artifact_id}.docx"
    pptx_file = ARTIFACTS_DIR / f"{artifact_id}.pptx"
    old_docx_file = old_artifacts_dir / f"{artifact_id}.docx"
    old_pptx_file = old_artifacts_dir / f"{artifact_id}.pptx"
    
    file_path = None
    media_type = None
    filename = None
    
    # Check new location first, then old location
    logger.debug(f"Looking for artifact {artifact_id}")
    logger.debug(f"  Checking: {docx_file} (exists: {docx_file.exists()})")
    logger.debug(f"  Checking: {pptx_file} (exists: {pptx_file.exists()})")
    logger.debug(f"  Checking old: {old_docx_file} (exists: {old_docx_file.exists()})")
    logger.debug(f"  Checking old: {old_pptx_file} (exists: {old_pptx_file.exists()})")
    
    if docx_file.exists():
        file_path = docx_file
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"{artifact_id}.docx"
    elif old_docx_file.exists():
        file_path = old_docx_file
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"{artifact_id}.docx"
    elif pptx_file.exists():
        file_path = pptx_file
        media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        filename = f"{artifact_id}.pptx"
    elif old_pptx_file.exists():
        file_path = old_pptx_file
        media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        filename = f"{artifact_id}.pptx"
    else:
        logger.error(f"Artifact {artifact_id} not found in {ARTIFACTS_DIR} or {old_artifacts_dir}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artifact not found. Checked: {ARTIFACTS_DIR} and {old_artifacts_dir}"
        )

    return FileResponse(
        path=str(file_path),
        media_type=media_type,
        filename=filename,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

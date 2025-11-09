"""
API endpoints for intake session management with PostgreSQL backend.

Provides REST endpoints for creating, retrieving, submitting, and managing
intake sessions according to the OpenAPI specification.
"""

from fastapi import APIRouter, HTTPException, Header, status, Depends
from typing import Annotated
from sqlalchemy.orm import Session

from services.content_intake.models.session import (
    CreateSessionRequest,
    Session as SessionResponse,
    SessionResponse as SessionResponseModel,
    SubmitSessionRequest,
    ArtifactsResponse,
)
from services.content_intake.services.session_service import SessionService
from services.content_intake.database.connection import get_db

router = APIRouter()


def get_session_service(db: Session = Depends(get_db)) -> SessionService:
    """Dependency to get session service with database session."""
    return SessionService(db)


@router.post("/sessions", response_model=SessionResponseModel, status_code=status.HTTP_201_CREATED)
async def create_session(
    request: CreateSessionRequest,
    idempotency_key: Annotated[str | None, Header()] = None,
    service: SessionService = Depends(get_session_service),
) -> SessionResponseModel:
    """
    Create a new intake session.

    Upload content payload and create a new intake session.
    Returns session_id for subsequent operations.
    """
    try:
        session = await service.create_session(request, idempotency_key)
        return SessionResponseModel(
            session_id=session.session_id,
            status=session.status,
            created_at=session.created_at,
            proposal_id=session.proposal_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/sessions/{session_id}", response_model=SessionResponseModel)
async def get_session(
    session_id: str,
    service: SessionService = Depends(get_session_service),
) -> SessionResponseModel:
    """
    Retrieve session metadata.

    Get session metadata, processing state, and downstream artifact references.
    """
    session = await service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    return SessionResponseModel(
        session_id=session.session_id,
        status=session.status,
        created_at=session.created_at,
        proposal_id=session.proposal_id,
        error_message=session.error_message,
    )


@router.post("/sessions/{session_id}/submit", response_model=SessionResponseModel)
async def submit_session(
    session_id: str,
    request: SubmitSessionRequest | None = None,
    idempotency_key: Annotated[str | None, Header()] = None,
    service: SessionService = Depends(get_session_service),
) -> SessionResponseModel:
    """
    Finalize content and trigger layout generation.

    Submits the session to the Gestalt Design Engine for layout generation.
    """
    try:
        request = request or SubmitSessionRequest()
        updated_session = await service.submit_session(
            session_id, request.layout_mode, idempotency_key
        )
        return SessionResponseModel(
            session_id=updated_session.session_id,
            status=updated_session.status,
            created_at=updated_session.created_at,
            proposal_id=updated_session.proposal_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/sessions/{session_id}/artifacts", response_model=ArtifactsResponse)
async def list_artifacts(
    session_id: str,
    service: SessionService = Depends(get_session_service),
) -> ArtifactsResponse:
    """
    List generated artifacts.

    Returns layout specifications and final document artifact IDs.
    """
    # First check if session exists
    session = await service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    artifacts = await service.get_artifacts(session_id)
    return ArtifactsResponse(session_id=session_id, artifacts=artifacts)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: str,
    service: SessionService = Depends(get_session_service),
) -> None:
    """
    Cancel and purge a session.

    Delete a session that has not been rendered yet.
    """
    try:
        await service.delete_session(session_id)
    except ValueError as e:
        # Check if it's "not found" error or "cannot delete" error
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

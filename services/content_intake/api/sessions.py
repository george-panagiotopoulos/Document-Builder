"""
API endpoints for intake session management.

Provides REST endpoints for creating, retrieving, submitting, and managing
intake sessions according to the OpenAPI specification.
"""

from fastapi import APIRouter, HTTPException, Header, status
from typing import Annotated

from services.content_intake.models.session import (
    CreateSessionRequest,
    Session,
    SessionResponse,
    SubmitSessionRequest,
    ArtifactsResponse,
)
from services.content_intake.services.session_service import SessionService

router = APIRouter()
session_service = SessionService()


@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    request: CreateSessionRequest,
    idempotency_key: Annotated[str | None, Header()] = None,
) -> SessionResponse:
    """
    Create a new intake session.

    Upload content payload and create a new intake session.
    Returns session_id for subsequent operations.
    """
    try:
        session = await session_service.create_session(request, idempotency_key)
        return SessionResponse(
            session_id=session.session_id,
            status=session.status,
            created_at=session.created_at,
            proposal_id=session.proposal_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str) -> SessionResponse:
    """
    Retrieve session metadata.

    Get session metadata, processing state, and downstream artifact references.
    """
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    return SessionResponse(
        session_id=session.session_id,
        status=session.status,
        created_at=session.created_at,
        proposal_id=session.proposal_id,
        error_message=session.error_message,
    )


@router.post("/sessions/{session_id}/submit", response_model=SessionResponse)
async def submit_session(
    session_id: str,
    request: SubmitSessionRequest | None = None,
    idempotency_key: Annotated[str | None, Header()] = None,
) -> SessionResponse:
    """
    Finalize content and trigger layout generation.

    Submits the session to the Gestalt Design Engine for layout generation.
    """
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    try:
        request = request or SubmitSessionRequest()
        updated_session = await session_service.submit_session(
            session_id, request.layout_mode, idempotency_key
        )
        return SessionResponse(
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
async def list_artifacts(session_id: str) -> ArtifactsResponse:
    """
    List generated artifacts.

    Returns layout specifications and final document artifact IDs.
    """
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    artifacts = await session_service.get_artifacts(session_id)
    return ArtifactsResponse(session_id=session_id, artifacts=artifacts)


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str) -> None:
    """
    Cancel and purge a session.

    Delete a session that has not been rendered yet.
    """
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

    try:
        await session_service.delete_session(session_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

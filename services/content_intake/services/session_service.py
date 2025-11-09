"""
Session service business logic.

Handles session creation, normalization, submission, and lifecycle management.
Coordinates calls to downstream services like the Gestalt Design Engine.
"""

from typing import Any

from services.content_intake.models.session import (
    CreateSessionRequest,
    Session,
    SessionStatus,
)


class SessionService:
    """Service for managing intake sessions."""

    def __init__(self) -> None:
        """Initialize session service with in-memory storage."""
        self._sessions: dict[str, Session] = {}
        self._idempotency_keys: dict[str, str] = {}

    async def create_session(
        self, request: CreateSessionRequest, idempotency_key: str | None = None
    ) -> Session:
        """
        Create a new intake session.

        Validates payload, normalizes content, and persists session state.
        """
        # Check idempotency
        if idempotency_key and idempotency_key in self._idempotency_keys:
            session_id = self._idempotency_keys[idempotency_key]
            return self._sessions[session_id]

        # Validate payload size
        total_blocks = len(request.content_blocks)
        total_images = len(request.images)

        if total_blocks > 1000:
            raise ValueError(f"Too many content blocks: {total_blocks} (max 1000)")
        if total_images > 200:
            raise ValueError(f"Too many images: {total_images} (max 200)")

        # Create session
        session = Session(
            content_blocks=request.content_blocks,
            images=request.images,
            design_intent=request.design_intent,
            constraints=request.constraints,
            status=SessionStatus.DRAFT,
        )

        # Normalize content
        await self._normalize_content(session)

        # Persist session
        self._sessions[session.session_id] = session

        # Store idempotency key
        if idempotency_key:
            self._idempotency_keys[idempotency_key] = session.session_id

        return session

    async def get_session(self, session_id: str) -> Session | None:
        """Retrieve session by ID."""
        return self._sessions.get(session_id)

    async def submit_session(
        self, session_id: str, layout_mode: str, idempotency_key: str | None = None
    ) -> Session:
        """
        Submit session for layout generation.

        Transitions session to layout_queued and triggers downstream processing.
        """
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")

        if session.status not in [SessionStatus.DRAFT, SessionStatus.READY]:
            raise ValueError(f"Cannot submit session in status {session.status}")

        # Update session status
        session.status = SessionStatus.LAYOUT_QUEUED

        # In a real implementation, this would call the Gestalt Design Engine
        # For now, we'll simulate by updating the status
        session.proposal_id = f"lsp-{session_id.split('-')[1]}"

        return session

    async def get_artifacts(self, session_id: str) -> list[dict[str, Any]]:
        """Get artifacts for a session."""
        session = self._sessions.get(session_id)
        if not session:
            return []

        artifacts: list[dict[str, Any]] = []

        # Return layout specification if available
        if session.proposal_id:
            artifacts.append(
                {
                    "artifact_id": session.proposal_id,
                    "type": "layout_specification",
                    "status": "complete" if session.status == SessionStatus.LAYOUT_COMPLETE else "pending",
                }
            )

        return artifacts

    async def delete_session(self, session_id: str) -> None:
        """Delete a session."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError("Session not found")

        if session.status == SessionStatus.LAYOUT_COMPLETE:
            raise ValueError("Cannot delete session that has been rendered")

        del self._sessions[session_id]

    async def _normalize_content(self, session: Session) -> None:
        """
        Normalize content blocks.

        Performs tokenization, structural detection, and enrichment.
        """
        # Detect structural cues and enrich metadata
        for block in session.content_blocks:
            # Calculate word count
            word_count = len(block.text.split())
            block.metrics["word_count"] = word_count

            # Estimate reading time (200 words per minute average)
            block.metrics["estimated_reading_seconds"] = int((word_count / 200) * 60)

            # Auto-detect role based on type and position
            if not block.detected_role:
                if block.type.value == "heading" and block.sequence == 0:
                    block.detected_role = "introduction"
                elif block.type.value == "callout":
                    block.detected_role = "action"
                else:
                    block.detected_role = "supporting"

        # Update session status
        session.status = SessionStatus.READY

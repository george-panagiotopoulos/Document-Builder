"""
Session service business logic with PostgreSQL integration.

Handles session creation, normalization, submission, and lifecycle management.
Coordinates calls to downstream services like the Gestalt Design Engine.
"""

from typing import Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from services.content_intake.models.session import (
    CreateSessionRequest,
    Session as SessionResponse,
    SessionStatus,
)
from services.content_intake.database.models import (
    SessionModel,
    ContentBlockModel,
    ImageAssetModel,
    IdempotencyKeyModel,
)


class SessionService:
    """Service for managing intake sessions with PostgreSQL backend."""

    def __init__(self, db: Session) -> None:
        """
        Initialize session service with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    async def create_session(
        self, request: CreateSessionRequest, idempotency_key: str | None = None
    ) -> SessionResponse:
        """
        Create a new intake session.

        Validates payload, normalizes content, and persists session state to PostgreSQL.
        """
        # Check idempotency
        if idempotency_key:
            existing = self.db.query(IdempotencyKeyModel).filter(
                IdempotencyKeyModel.idempotency_key == idempotency_key
            ).first()
            if existing:
                session_model = self.db.query(SessionModel).filter(
                    SessionModel.session_id == existing.session_id
                ).first()
                return self._model_to_response(session_model)

        # Validate payload size
        total_blocks = len(request.content_blocks)
        total_images = len(request.images)

        if total_blocks > 1000:
            raise ValueError(f"Too many content blocks: {total_blocks} (max 1000)")
        if total_images > 200:
            raise ValueError(f"Too many images: {total_images} (max 200)")

        # Create session model
        from uuid import uuid4
        session_id = f"sess-{uuid4().hex}"

        session_model = SessionModel(
            session_id=session_id,
            status=SessionStatus.DRAFT,
            design_intent=request.design_intent.model_dump(),
            constraints=request.constraints.model_dump() if request.constraints else {},
        )

        self.db.add(session_model)
        self.db.flush()  # Get session_id before creating related records

        # Create content blocks
        for block in request.content_blocks:
            block_model = ContentBlockModel(
                block_id=block.block_id,
                session_id=session_id,
                type=block.type.value,
                level=block.level,
                sequence=block.sequence,
                text=block.text,
                language=block.language,
                detected_role=block.detected_role,
                metrics=block.metrics,
            )
            self.db.add(block_model)

        # Create image assets
        for image in request.images:
            image_model = ImageAssetModel(
                image_id=image.image_id,
                session_id=session_id,
                uri=image.uri,
                format=image.format,
                width_px=image.width_px,
                height_px=image.height_px,
                alt_text=image.alt_text,
                content_role=image.content_role,
                dominant_palette=image.dominant_palette,
            )
            self.db.add(image_model)

        # Normalize content
        await self._normalize_content(session_model)

        # Store idempotency key
        if idempotency_key:
            idem_key = IdempotencyKeyModel(
                idempotency_key=idempotency_key,
                session_id=session_id,
                expires_at=datetime.utcnow() + timedelta(hours=24),
            )
            self.db.add(idem_key)

        self.db.commit()
        self.db.refresh(session_model)

        return self._model_to_response(session_model)

    async def get_session(self, session_id: str) -> SessionResponse | None:
        """Retrieve session by ID."""
        session_model = self.db.query(SessionModel).filter(
            SessionModel.session_id == session_id
        ).first()

        if not session_model:
            return None

        return self._model_to_response(session_model)

    async def submit_session(
        self, session_id: str, layout_mode: str, idempotency_key: str | None = None
    ) -> SessionResponse:
        """
        Submit session for layout generation.

        Transitions session to layout_queued and triggers downstream processing.
        """
        session_model = self.db.query(SessionModel).filter(
            SessionModel.session_id == session_id
        ).first()

        if not session_model:
            raise ValueError("Session not found")

        if session_model.status not in [SessionStatus.DRAFT, SessionStatus.READY]:
            raise ValueError(f"Cannot submit session in status {session_model.status}")

        # Update session status
        session_model.status = SessionStatus.LAYOUT_QUEUED
        session_model.proposal_id = f"lsp-{session_id.split('-')[1]}"
        session_model.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(session_model)

        return self._model_to_response(session_model)

    async def get_artifacts(self, session_id: str) -> list[dict[str, Any]]:
        """Get artifacts for a session."""
        session_model = self.db.query(SessionModel).filter(
            SessionModel.session_id == session_id
        ).first()

        if not session_model:
            return []

        artifacts: list[dict[str, Any]] = []

        # Return layout specification if available
        if session_model.proposal_id:
            artifacts.append(
                {
                    "artifact_id": session_model.proposal_id,
                    "type": "layout_specification",
                    "status": "complete" if session_model.status == SessionStatus.LAYOUT_COMPLETE else "pending",
                }
            )

        return artifacts

    async def delete_session(self, session_id: str) -> None:
        """Delete a session and all related data (cascading)."""
        session_model = self.db.query(SessionModel).filter(
            SessionModel.session_id == session_id
        ).first()

        if not session_model:
            raise ValueError("Session not found")

        if session_model.status == SessionStatus.LAYOUT_COMPLETE:
            raise ValueError("Cannot delete session that has been rendered")

        self.db.delete(session_model)
        self.db.commit()

    async def _normalize_content(self, session_model: SessionModel) -> None:
        """
        Normalize content blocks.

        Performs tokenization, structural detection, and enrichment.
        """
        # Refresh to get content blocks
        self.db.refresh(session_model)

        # Detect structural cues and enrich metadata
        for block in session_model.content_blocks:
            # Calculate word count
            word_count = len(block.text.split())
            if not block.metrics:
                block.metrics = {}
            block.metrics["word_count"] = word_count

            # Estimate reading time (200 words per minute average)
            block.metrics["estimated_reading_seconds"] = int((word_count / 200) * 60)

            # Auto-detect role based on type and position
            if not block.detected_role:
                if block.type == "heading" and block.sequence == 0:
                    block.detected_role = "introduction"
                elif block.type == "callout":
                    block.detected_role = "action"
                else:
                    block.detected_role = "supporting"

        # Update session status
        session_model.status = SessionStatus.READY
        session_model.updated_at = datetime.utcnow()

    def _model_to_response(self, session_model: SessionModel) -> SessionResponse:
        """Convert database model to response model."""
        from services.content_intake.models.session import ContentBlock, ImageAsset, DesignIntent, Constraints

        # Convert content blocks
        content_blocks = []
        for block_model in session_model.content_blocks:
            content_blocks.append(
                ContentBlock(
                    block_id=block_model.block_id,
                    type=block_model.type,
                    level=block_model.level,
                    sequence=block_model.sequence,
                    text=block_model.text,
                    language=block_model.language,
                    detected_role=block_model.detected_role,
                    metrics=block_model.metrics or {},
                )
            )

        # Convert images
        images = []
        for image_model in session_model.images:
            images.append(
                ImageAsset(
                    image_id=image_model.image_id,
                    uri=image_model.uri,
                    format=image_model.format,
                    width_px=image_model.width_px,
                    height_px=image_model.height_px,
                    alt_text=image_model.alt_text,
                    content_role=image_model.content_role,
                    dominant_palette=image_model.dominant_palette or [],
                )
            )

        return SessionResponse(
            session_id=session_model.session_id,
            status=session_model.status,
            created_at=session_model.created_at,
            created_by=session_model.created_by,
            content_blocks=content_blocks,
            images=images,
            design_intent=DesignIntent(**session_model.design_intent),
            constraints=Constraints(**session_model.constraints) if session_model.constraints else Constraints(),
            proposal_id=session_model.proposal_id,
            error_message=session_model.error_message,
        )

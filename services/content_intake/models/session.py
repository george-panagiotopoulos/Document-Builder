"""
Data models for intake sessions.

Defines the core data structures for managing content intake sessions,
including session metadata, content blocks, images, and intent descriptors.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class SessionStatus(str, Enum):
    """Session lifecycle states."""

    DRAFT = "draft"
    NORMALIZING = "normalizing"
    READY = "ready"
    LAYOUT_QUEUED = "layout_queued"
    LAYOUT_PROCESSING = "layout_processing"
    LAYOUT_COMPLETE = "layout_complete"
    FAILED = "failed"


class ContentBlockType(str, Enum):
    """Content block types."""

    HEADING = "heading"
    PARAGRAPH = "paragraph"
    LIST = "list"
    QUOTE = "quote"
    TABLE = "table"
    CALLOUT = "callout"


class ContentBlock(BaseModel):
    """Represents a single content block."""

    block_id: str = Field(default_factory=lambda: f"block-{uuid4().hex[:8]}")
    type: ContentBlockType
    level: int = Field(default=0, ge=0, le=6)
    sequence: int = Field(ge=0)
    text: str = Field(max_length=10000)
    language: str = Field(default="en", pattern=r"^[a-z]{2}$")
    detected_role: str | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)


class ImageAsset(BaseModel):
    """Represents an image asset."""

    image_id: str = Field(default_factory=lambda: f"img-{uuid4().hex[:8]}")
    uri: str
    format: str = Field(pattern=r"^(png|jpg|jpeg|svg)$")
    width_px: int = Field(gt=0, le=4096)
    height_px: int = Field(gt=0, le=4096)
    alt_text: str = Field(max_length=500)
    content_role: str = Field(default="illustration")
    dominant_palette: list[str] = Field(default_factory=list)


class DesignIntent(BaseModel):
    """Design intent metadata."""

    purpose: str = Field(pattern=r"^(report|presentation|proposal|playbook)$")
    audience: str = Field(pattern=r"^(executive|technical|customer|internal)$")
    tone: str = Field(default="formal", pattern=r"^(formal|conversational|persuasive|educational)$")
    goals: list[str] = Field(default_factory=lambda: ["clarity"])
    primary_actions: list[str] = Field(default_factory=list)
    success_metrics: list[str] = Field(default_factory=list)


class Constraints(BaseModel):
    """Design constraints and preferences."""

    visual_density: str = Field(
        default="balanced", pattern=r"^(tight|balanced|airy)$"
    )
    color_policy: dict[str, Any] = Field(default_factory=dict)
    brand_guidelines: dict[str, Any] = Field(default_factory=dict)
    document_preferences: dict[str, Any] = Field(default_factory=dict)
    presentation_preferences: dict[str, Any] = Field(default_factory=dict)


class CreateSessionRequest(BaseModel):
    """Request to create a new intake session."""

    content_blocks: list[ContentBlock] = Field(min_length=1, max_length=1000)
    images: list[ImageAsset] = Field(default_factory=list, max_length=200)
    design_intent: DesignIntent
    constraints: Constraints = Field(default_factory=Constraints)


class SubmitSessionRequest(BaseModel):
    """Request to submit a session for layout generation."""

    layout_mode: str = Field(default="rule_only", pattern=r"^(rule_only|ai_assist|ai_full)$")


class Session(BaseModel):
    """Intake session with full metadata."""

    session_id: str = Field(default_factory=lambda: f"sess-{uuid4().hex}")
    status: SessionStatus = SessionStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str | None = None
    content_blocks: list[ContentBlock]
    images: list[ImageAsset]
    design_intent: DesignIntent
    constraints: Constraints
    proposal_id: str | None = None
    error_message: str | None = None


class SessionResponse(BaseModel):
    """Response containing session details."""

    session_id: str
    status: SessionStatus
    created_at: datetime
    proposal_id: str | None = None
    error_message: str | None = None


class ArtifactsResponse(BaseModel):
    """Response containing artifacts list."""

    session_id: str
    artifacts: list[dict[str, Any]]

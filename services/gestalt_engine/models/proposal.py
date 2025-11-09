"""
Data models for layout proposals and specifications.

Defines the Layout Specification Package (LSP) structure and related models.
"""

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class ProposalStatus(str, Enum):
    """Proposal lifecycle states."""

    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETE = "complete"
    FAILED = "failed"


class DocumentType(str, Enum):
    """Document types."""

    WORD = "word"
    POWERPOINT = "powerpoint"


class ElementType(str, Enum):
    """Layout element types."""

    TEXT = "text"
    IMAGE = "image"
    TABLE = "table"
    SHAPE = "shape"
    CHART = "chart"


class Position(BaseModel):
    """Element position coordinates."""

    x: float = Field(ge=0, description="X coordinate in inches")
    y: float = Field(ge=0, description="Y coordinate in inches")
    width: float = Field(gt=0, description="Width in inches")
    height: float = Field(gt=0, description="Height in inches")
    z_index: int = Field(default=0, ge=0, description="Stacking order")


class GridPosition(BaseModel):
    """Grid-based positioning."""

    column_start: int = Field(ge=1, le=12)
    column_span: int = Field(ge=1, le=12)
    row_start: int = Field(ge=1)
    row_span: int = Field(default=1, ge=1)


class Font(BaseModel):
    """Font styling."""

    family: str = Field(default="Arial")
    size_pt: int = Field(default=11, ge=6, le=72)
    weight: str = Field(default="normal", pattern=r"^(normal|medium|semibold|bold)$")
    style: str = Field(default="normal", pattern=r"^(normal|italic)$")
    caps: str = Field(default="none")


class Spacing(BaseModel):
    """Spacing configuration."""

    margin_top: float = Field(default=0.0, ge=0)
    margin_bottom: float = Field(default=0.0, ge=0)
    margin_left: float = Field(default=0.0, ge=0)
    margin_right: float = Field(default=0.0, ge=0)
    line_height: float = Field(default=1.2, ge=1.0, le=3.0)


class Styling(BaseModel):
    """Element styling configuration."""

    font: Font | None = None
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    background: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    alignment: str = Field(default="left", pattern=r"^(left|center|right|justify)$")
    spacing: Spacing = Field(default_factory=Spacing)


class GestaltRules(BaseModel):
    """Gestalt principle tags for an element."""

    hierarchy_level: int = Field(ge=1, le=5)
    proximity_group: str | None = None
    similarity_family: str | None = None


class LayoutElement(BaseModel):
    """A single layout element."""

    element_id: str = Field(default_factory=lambda: f"elem-{uuid4().hex[:8]}")
    content_ref: str | None = None
    role: str | None = None
    type: ElementType
    position: Position
    grid: GridPosition | None = None
    styling: Styling
    gestalt_rules: GestaltRules | None = None
    behaviors: dict[str, Any] = Field(default_factory=dict)


class StructureUnit(BaseModel):
    """A structural unit (page, slide, or section)."""

    unit_id: str = Field(default_factory=lambda: f"unit-{uuid4().hex[:8]}")
    type: str = Field(pattern=r"^(section|page|slide)$")
    title: str | None = None
    template: str
    elements: list[LayoutElement] = Field(default_factory=list, max_length=50)
    notes: str | None = None


class DesignRationale(BaseModel):
    """Design rationale and scoring."""

    principles_applied: list[str] = Field(default_factory=list)
    scores: dict[str, float] = Field(default_factory=dict)
    quality_grade: str | None = Field(
        None, pattern=r"^(excellent|good|acceptable|needs_improvement)$"
    )
    ai_contributions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class LayoutSpecificationPackage(BaseModel):
    """Complete Layout Specification Package (LSP)."""

    schema_version: str = Field(default="1.1")
    proposal_id: str
    session_id: str
    document_type: DocumentType
    metadata: dict[str, Any] = Field(default_factory=dict)
    structure: list[StructureUnit]
    design_rationale: DesignRationale = Field(default_factory=DesignRationale)
    warnings: list[str] = Field(default_factory=list)
    formatter_overrides: dict[str, Any] = Field(default_factory=dict)


class ProposalResponse(BaseModel):
    """Response for proposal status."""

    proposal_id: str
    status: ProposalStatus
    estimated_completion_seconds: int | None = None
    error: str | None = None

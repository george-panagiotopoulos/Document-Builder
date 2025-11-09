"""SQLAlchemy database models for Content Intake Service."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Enum as SQLEnum, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
import enum

from services.content_intake.database.connection import Base


class SessionStatusEnum(str, enum.Enum):
    """Session lifecycle states."""
    DRAFT = "draft"
    NORMALIZING = "normalizing"
    READY = "ready"
    LAYOUT_QUEUED = "layout_queued"
    LAYOUT_PROCESSING = "layout_processing"
    LAYOUT_COMPLETE = "layout_complete"
    FAILED = "failed"


class SessionModel(Base):
    """Database model for intake sessions."""

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    status = Column(SQLEnum(SessionStatusEnum), default=SessionStatusEnum.DRAFT, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String(255), nullable=True)

    # Intent and constraints stored as JSON
    design_intent = Column(JSON, nullable=False)
    constraints = Column(JSON, nullable=True)

    # Downstream references
    proposal_id = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    content_blocks = relationship("ContentBlockModel", back_populates="session", cascade="all, delete-orphan")
    images = relationship("ImageAssetModel", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Session {self.session_id} status={self.status}>"


class ContentBlockModel(Base):
    """Database model for content blocks."""

    __tablename__ = "content_blocks"

    id = Column(Integer, primary_key=True, index=True)
    block_id = Column(String(100), unique=True, index=True, nullable=False)
    session_id = Column(String(100), ForeignKey("sessions.session_id"), nullable=False)

    type = Column(String(50), nullable=False)
    level = Column(Integer, default=0, nullable=False)
    sequence = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    language = Column(String(2), default="en", nullable=False)
    detected_role = Column(String(50), nullable=True)

    # Metrics stored as JSON
    metrics = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    session = relationship("SessionModel", back_populates="content_blocks")

    def __repr__(self) -> str:
        return f"<ContentBlock {self.block_id} type={self.type}>"


class ImageAssetModel(Base):
    """Database model for image assets."""

    __tablename__ = "image_assets"

    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(String(100), unique=True, index=True, nullable=False)
    session_id = Column(String(100), ForeignKey("sessions.session_id"), nullable=False)

    uri = Column(String(500), nullable=False)
    format = Column(String(10), nullable=False)
    width_px = Column(Integer, nullable=False)
    height_px = Column(Integer, nullable=False)
    alt_text = Column(String(500), nullable=False)
    content_role = Column(String(50), default="illustration", nullable=False)

    # Palette stored as JSON array
    dominant_palette = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship
    session = relationship("SessionModel", back_populates="images")

    def __repr__(self) -> str:
        return f"<ImageAsset {self.image_id} format={self.format}>"


class IdempotencyKeyModel(Base):
    """Database model for idempotency keys."""

    __tablename__ = "idempotency_keys"

    id = Column(Integer, primary_key=True, index=True)
    idempotency_key = Column(String(255), unique=True, index=True, nullable=False)
    session_id = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<IdempotencyKey {self.idempotency_key} -> {self.session_id}>"

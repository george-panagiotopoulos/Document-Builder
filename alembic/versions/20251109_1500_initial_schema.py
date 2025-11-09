"""Initial database schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2025-11-09 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=100), nullable=False),
        sa.Column('status', sa.Enum('draft', 'normalizing', 'ready', 'layout_queued', 'layout_processing', 'layout_complete', 'failed', name='sessionstatusenum'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('design_intent', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('constraints', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('proposal_id', sa.String(length=100), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id')
    )
    op.create_index(op.f('ix_sessions_session_id'), 'sessions', ['session_id'], unique=True)

    # Create content_blocks table
    op.create_table(
        'content_blocks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('block_id', sa.String(length=100), nullable=False),
        sa.Column('session_id', sa.String(length=100), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('sequence', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('language', sa.String(length=2), nullable=False),
        sa.Column('detected_role', sa.String(length=50), nullable=True),
        sa.Column('metrics', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('block_id')
    )
    op.create_index(op.f('ix_content_blocks_block_id'), 'content_blocks', ['block_id'], unique=True)

    # Create image_assets table
    op.create_table(
        'image_assets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('image_id', sa.String(length=100), nullable=False),
        sa.Column('session_id', sa.String(length=100), nullable=False),
        sa.Column('uri', sa.String(length=500), nullable=False),
        sa.Column('format', sa.String(length=10), nullable=False),
        sa.Column('width_px', sa.Integer(), nullable=False),
        sa.Column('height_px', sa.Integer(), nullable=False),
        sa.Column('alt_text', sa.String(length=500), nullable=False),
        sa.Column('content_role', sa.String(length=50), nullable=False),
        sa.Column('dominant_palette', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.session_id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('image_id')
    )
    op.create_index(op.f('ix_image_assets_image_id'), 'image_assets', ['image_id'], unique=True)

    # Create idempotency_keys table
    op.create_table(
        'idempotency_keys',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('idempotency_key', sa.String(length=255), nullable=False),
        sa.Column('session_id', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('idempotency_key')
    )
    op.create_index(op.f('ix_idempotency_keys_idempotency_key'), 'idempotency_keys', ['idempotency_key'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_idempotency_keys_idempotency_key'), table_name='idempotency_keys')
    op.drop_table('idempotency_keys')
    op.drop_index(op.f('ix_image_assets_image_id'), table_name='image_assets')
    op.drop_table('image_assets')
    op.drop_index(op.f('ix_content_blocks_block_id'), table_name='content_blocks')
    op.drop_table('content_blocks')
    op.drop_index(op.f('ix_sessions_session_id'), table_name='sessions')
    op.drop_table('sessions')
    op.execute('DROP TYPE sessionstatusenum')

"""Convert status enum to varchar

Revision ID: 002_convert_status_to_varchar
Revises: 001_initial_schema
Create Date: 2025-11-09 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_convert_status_to_varchar'
down_revision: str = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Convert enum column to VARCHAR
    # First, alter the column type to VARCHAR
    op.execute("""
        ALTER TABLE sessions 
        ALTER COLUMN status TYPE VARCHAR(50) 
        USING status::text
    """)
    
    # Drop the enum type (optional, but cleans up)
    op.execute('DROP TYPE IF EXISTS sessionstatusenum')


def downgrade() -> None:
    # Recreate the enum type
    op.execute("""
        CREATE TYPE sessionstatusenum AS ENUM (
            'draft', 'normalizing', 'ready', 'layout_queued', 
            'layout_processing', 'layout_complete', 'failed'
        )
    """)
    
    # Convert VARCHAR column back to enum
    op.execute("""
        ALTER TABLE sessions 
        ALTER COLUMN status TYPE sessionstatusenum 
        USING status::sessionstatusenum
    """)


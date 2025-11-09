#!/usr/bin/env python
"""
Database initialization script.

Run migrations and initialize the database for Content Intake Service.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from alembic import command
from alembic.config import Config
from services.content_intake.database.connection import init_db
from services.content_intake.utils.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def run_migrations() -> None:
    """Run Alembic migrations."""
    logger.info("Running database migrations...")

    # Alembic needs to be run from the infrastructure directory
    # because script_location is relative to alembic.ini location
    import os
    original_dir = os.getcwd()
    try:
        os.chdir("infrastructure")
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
    finally:
        os.chdir(original_dir)

    logger.info("Migrations completed successfully")


def initialize_database() -> None:
    """Initialize database and run migrations."""
    logger.info("Initializing Content Intake Service database...")

    try:
        # Run migrations
        run_migrations()

        logger.info("Database initialization complete!")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


if __name__ == "__main__":
    initialize_database()

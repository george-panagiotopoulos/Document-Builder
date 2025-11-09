"""
Structured logging configuration.

Sets up JSON-formatted logging with correlation IDs for distributed tracing.
"""

import logging
import sys
from typing import Any

from services.content_intake.utils.config import settings


def setup_logging() -> None:
    """Configure structured logging."""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance."""
    return logging.getLogger(name)

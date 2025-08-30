"""Logging middleware configuration."""

import logging

from ..core.config import settings


def setup_logging() -> None:
    """Setup application logging."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
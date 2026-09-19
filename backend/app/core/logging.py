"""Structured application logging setup.

Configures a consistent logging format across all modules.
Log levels are controlled via the LOG_LEVEL environment variable.

Usage:
    from app.core.logging import get_logger
    logger = get_logger(__name__)
    logger.info("Run created", extra={"run_id": run_id})

Security:
    Never log API keys, secrets, or authentication tokens.
"""

import logging
import sys

from app.core.config import get_settings


def setup_logging() -> None:
    """Configure root logger with structured format and appropriate level."""
    settings = get_settings()

    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    )
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a named logger instance.

    Args:
        name: Logger name, typically __name__ of the calling module.

    Returns:
        Configured logger instance.
    """
    return logging.getLogger(name)

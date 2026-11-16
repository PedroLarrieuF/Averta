"""Logging configuration for the automation."""

import sys
from pathlib import Path
from loguru import logger
from .config_loader import get_settings


def setup_logging() -> None:
    """Configure logging based on settings."""
    settings = get_settings()

    # Remove default handler
    logger.remove()

    # Ensure log directory exists
    log_file = Path(settings.logging_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Add file handler
    logger.add(
        settings.logging_file,
        level=settings.logging_level,
        format=settings.logging_format,
        rotation=settings.logging_rotation,
        retention=settings.logging_retention,
        compression=settings.logging_compression,
        encoding="utf-8",
        backtrace=True,
        diagnose=True,
    )

    # Add console handler if enabled
    if settings.logging_console:
        logger.add(
            sys.stdout,
            level=settings.logging_level,
            format=settings.logging_format,
            colorize=True,
            backtrace=True,
            diagnose=True,
        )

    logger.info(f"Logging configured - Level: {settings.logging_level}")


def get_logger(name: str):
    """Get a logger instance for a module."""
    return logger.bind(name=name)


# Initialize logging on import
setup_logging()
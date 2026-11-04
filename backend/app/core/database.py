"""Database connection using Prisma Client Python"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog

from prisma import Prisma

logger = structlog.get_logger()

# Global Prisma client instance
_prisma: Prisma | None = None


def _get_prisma_instance() -> Prisma:
    """Get or create Prisma client instance."""
    global _prisma  # noqa: PLW0603
    if _prisma is None:
        _prisma = Prisma()
    return _prisma


async def get_prisma() -> Prisma:
    """Get Prisma client instance"""
    prisma = _get_prisma_instance()
    if not prisma.is_connected():
        await prisma.connect()
        logger.info("database_connected")
    return prisma


async def close_prisma() -> None:
    """Close Prisma connection"""
    global _prisma  # noqa: PLW0603
    if _prisma is not None and _prisma.is_connected():
        await _prisma.disconnect()
        _prisma = None
        logger.info("database_disconnected")


@asynccontextmanager
async def lifespan_db() -> AsyncGenerator["Prisma", None]:
    """Lifespan context manager for database"""
    client = await get_prisma()
    try:
        yield client
    finally:
        await close_prisma()


# Dependency for FastAPI
async def get_db() -> AsyncGenerator["Prisma", None]:
    """FastAPI dependency for database"""
    client = await get_prisma()
    try:
        yield client
    except Exception:
        # Prisma handles connection pooling automatically
        raise

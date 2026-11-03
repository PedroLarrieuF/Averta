"""Database connection using Prisma Client Python"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prisma import Prisma

import structlog

from app.core.config import settings

logger = structlog.get_logger()

# Global Prisma client instance
prisma: "Prisma" = None


async def get_prisma() -> "Prisma":
    """Get Prisma client instance"""
    global prisma
    if prisma is None:
        # Import here to avoid import-time errors
        from prisma import Prisma as PrismaClient

        prisma = PrismaClient(
            datasource={"url": settings.DATABASE_URL},
            auto_register=True,
            log_queries=settings.DEBUG,
        )
        await prisma.connect()
        logger.info("database_connected")
    return prisma


async def close_prisma() -> None:
    """Close Prisma connection"""
    global prisma
    if prisma is not None:
        await prisma.disconnect()
        prisma = None
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

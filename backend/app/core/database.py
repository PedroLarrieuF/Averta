"""Database connection using Prisma Client Python with Connection Pooling, Read Replica & Query Logging"""

import asyncio
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog

from app.core.config import settings
from generated.prisma import Prisma
from prisma.types import QueryEvent

logger = structlog.get_logger()

# Constants
SLOW_QUERY_THRESHOLD_MS: int = 500

# Global Prisma client instances
_prisma_primary: Prisma | None = None
_prisma_replica: Prisma | None = None


def _get_prisma_primary() -> Prisma:
    """Get or create primary Prisma client instance (write operations)."""
    global _prisma_primary  # noqa: PLW0603
    if _prisma_primary is None:
        _prisma_primary = Prisma(
            datasource={
                "url": settings.DATABASE_URL,
            },
            # Connection pool settings for PgBouncer (transaction mode)
            # pool_size = (cpu_cores * 4) + 1, but we use env var
            connect_timeout=settings.DATABASE_CONNECT_TIMEOUT,
            # Engine settings
            engine_type="binary",  # Better performance than 'node'
        )
    return _prisma_primary


def _get_prisma_replica() -> Prisma:
    """Get or create read replica Prisma client instance (read operations)."""
    global _prisma_replica  # noqa: PLW0603
    if _prisma_replica is None and settings.DATABASE_READ_REPLICA_URL:
        _prisma_replica = Prisma(
            datasource={
                "url": settings.DATABASE_READ_REPLICA_URL,
            },
            connect_timeout=settings.DATABASE_CONNECT_TIMEOUT,
            engine_type="binary",
        )
    return _prisma_replica


async def _query_middleware(event: QueryEvent) -> None:
    """Middleware for query logging and slow query detection."""
    start_time = time.perf_counter()
    yield
    duration_ms = (time.perf_counter() - start_time) * 1000

    # Log all queries in development
    if settings.ENVIRONMENT == "development":
        logger.debug(
            "prisma_query",
            query=event.query,
            params=event.params,
            duration_ms=round(duration_ms, 2),
        )

    # Log slow queries in all environments
    if duration_ms > SLOW_QUERY_THRESHOLD_MS:
        logger.warning(
            "slow_query_detected",
            query=event.query,
            params=event.params,
            duration_ms=round(duration_ms, 2),
            model=event.model,
            action=event.action,
        )


async def get_prisma(use_replica: bool = False) -> Prisma:
    """
    Get Prisma client instance.

    Args:
        use_replica: If True, use read replica for SELECT queries.
                     Falls back to primary if replica unavailable.
    """
    # Try read replica for read operations
    if use_replica and settings.DATABASE_READ_REPLICA_URL:
        replica = _get_prisma_replica()
        if replica and replica.is_connected():
            return replica
        # Fallback to primary if replica not connected
        logger.warning("read_replica_unavailable_fallback_to_primary")

    primary = _get_prisma_primary()
    if not primary.is_connected():
        await primary.connect()
        logger.info("database_connected", instance="primary")
    return primary


async def get_prisma_primary() -> Prisma:
    """Get primary Prisma client (for write operations)."""
    return await get_prisma(use_replica=False)


async def get_prisma_replica() -> Prisma:
    """Get read replica Prisma client (for read operations)."""
    return await get_prisma(use_replica=True)


async def close_prisma() -> None:
    """Close all Prisma connections."""
    global _prisma_primary, _prisma_replica  # noqa: PLW0603

    if _prisma_primary is not None and _prisma_primary.is_connected():
        await _prisma_primary.disconnect()
        _prisma_primary = None
        logger.info("database_disconnected", instance="primary")

    if _prisma_replica is not None and _prisma_replica.is_connected():
        await _prisma_replica.disconnect()
        _prisma_replica = None
        logger.info("database_disconnected", instance="replica")


@asynccontextmanager
async def lifespan_db() -> AsyncGenerator["Prisma", None]:
    """Lifespan context manager for database (primary)."""
    client = await get_prisma_primary()
    try:
        yield client
    finally:
        await close_prisma()


# FastAPI Dependencies
async def get_db() -> AsyncGenerator["Prisma", None]:
    """FastAPI dependency for primary database (write operations)."""
    client = await get_prisma_primary()
    try:
        yield client
    except Exception:
        raise


async def get_db_read() -> AsyncGenerator["Prisma", None]:
    """FastAPI dependency for read replica database (read operations)."""
    client = await get_prisma_replica()
    try:
        yield client
    except Exception:
        raise


# Helper for services to choose the right client
def get_db_client(read_only: bool = False) -> Prisma:
    """
    Get appropriate DB client based on operation type.
    Usage: db = get_db_client(read_only=True)
    """
    if read_only:
        return asyncio.get_event_loop().run_until_complete(get_prisma_replica())
    return asyncio.get_event_loop().run_until_complete(get_prisma_primary())

"""Redis-backed rate limiter using slowapi with sliding window algorithm."""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, FastAPI
from app.core.config import settings
import structlog

logger = structlog.get_logger()

# Redis client for rate limiting (uses same REDIS_URL as Celery/cache)
# slowapi will use this storage_uri for distributed rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    default_limits=[f"{settings.RATE_LIMIT_REQUESTS}/minute"],
    strategy="sliding-window",
    headers_enabled=True,
)


def init_rate_limiter(app: FastAPI) -> None:
    """Initialize rate limiter on FastAPI app."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Log rate limit configuration
    logger.info(
        "rate_limiter_initialized",
        storage_uri=settings.REDIS_URL,
        default_limit=f"{settings.RATE_LIMIT_REQUESTS}/minute",
        strategy="sliding-window",
    )


# Endpoint-specific limiters
# These can be used as dependencies on specific routes
auth_limiter = limiter.limit("10/minute")
upload_limiter = limiter.limit("5/minute")
api_limiter = limiter.limit("100/minute")
reports_limiter = limiter.limit("20/minute")
discrepancies_limiter = limiter.limit("50/minute")
contests_limiter = limiter.limit("30/minute")


def get_limiter() -> Limiter:
    """Dependency to get the limiter instance."""
    return limiter


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Custom handler for rate limit exceeded with structured logging."""
    client_ip = get_remote_address(request)
    logger.warning(
        "rate_limit_exceeded",
        client_ip=client_ip,
        path=request.url.path,
        method=request.method,
        limit=exc.detail,
    )
    return await _rate_limit_exceeded_handler(request, exc)
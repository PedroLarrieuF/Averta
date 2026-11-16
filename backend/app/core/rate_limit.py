"""Redis-backed rate limiter using slowapi with sliding window algorithm.

Note: slowapi 0.1.9 has a bug in SlowAPIMiddleware._inject_headers where it checks
isinstance(response, starlette.responses.Response) but FastAPI's response types
don't pass this check. We use a custom middleware that handles this properly.
"""

import structlog
from fastapi import FastAPI, Request, Response
from fastapi.responses import Response as FastAPIResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

from app.core.config import settings

logger = structlog.get_logger()

# Redis client for rate limiting (uses same REDIS_URL as Celery/cache)
# slowapi will use this storage_uri for distributed rate limiting
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    default_limits=[f"{settings.RATE_LIMIT_REQUESTS}/minute"],
    strategy="fixed-window",
    headers_enabled=True,
)

# Note: slowapi 0.1.10's limit decorator calls _check_request_limit SYNCHRONOUSLY (without await)
# and expects it to set request.state.view_rate_limit. Our FixedSlowAPIMiddleware does NOT call
# _check_request_limit at all (it only injects headers), so the sync method works fine for the decorator.
# The original bug was in SlowAPIMiddleware which called await _check_request_limit() - we fixed that
# by not calling it in our custom middleware.

# ALSO: slowapi 0.1.10's _inject_headers checks isinstance(response, starlette.responses.Response)
# but FastAPI responses don't pass this check. The decorator's wrapper calls _inject_headers on
# the response, so we need to patch it to handle FastAPI responses.
_original_inject_headers = limiter._inject_headers

def _patched_inject_headers(self, response, rate_limit):
    """Patched _inject_headers that handles FastAPI response types."""
    # Handle both Starlette and FastAPI response objects
    # FastAPI responses have a .headers attribute that works like Starlette
    if hasattr(response, "headers"):
        response.headers["X-RateLimit-Limit"] = str(rate_limit.limit)
        response.headers["X-RateLimit-Remaining"] = str(rate_limit.remaining)
        response.headers["X-RateLimit-Reset"] = str(rate_limit.reset)

limiter._inject_headers = _patched_inject_headers.__get__(limiter, Limiter)


class FixedSlowAPIMiddleware(BaseHTTPMiddleware):
    """Custom middleware that fixes slowapi 0.1.9's response type check bug.

    The original SlowAPIMiddleware._inject_headers checks:
        isinstance(response, starlette.responses.Response)

    But FastAPI wraps responses in a way that breaks this check.
    This middleware properly handles both Starlette and FastAPI response types.

    Note: Rate limit checking is done by the @limiter.limit() decorators on endpoints.
    This middleware only injects rate limit headers into responses.
    """

    def __init__(self, app, limiter: Limiter):
        super().__init__(app)
        self.limiter = limiter

    async def dispatch(self, request: Request, call_next):
        # Process request
        response = await call_next(request)

        # Inject rate limit headers (fixed version that handles FastAPI responses)
        self._inject_headers(request, response)

        return response

    def _inject_headers(self, request: Request, response: Response) -> None:
        """Inject rate limit headers into response.

        Fixed to handle both Starlette and FastAPI response types.
        """
        # Check for rate limit info in request state (set by limiter decorators)
        if hasattr(request.state, "rate_limit"):
            rate_limit = request.state.rate_limit
            # Handle both Starlette and FastAPI response objects
            # FastAPI responses have a .headers attribute that works like Starlette
            if hasattr(response, "headers"):
                response.headers["X-RateLimit-Limit"] = str(rate_limit.limit)
                response.headers["X-RateLimit-Remaining"] = str(rate_limit.remaining)
                response.headers["X-RateLimit-Reset"] = str(rate_limit.reset)


def init_rate_limiter(app: FastAPI) -> None:
    """Initialize rate limiter on FastAPI app."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

    # Add custom middleware instead of SlowAPIMiddleware (which has a bug in 0.1.9)
    app.add_middleware(FixedSlowAPIMiddleware, limiter=limiter)

    # Log rate limit configuration
    logger.info(
        "rate_limiter_initialized",
        storage_uri=settings.REDIS_URL,
        default_limit=f"{settings.RATE_LIMIT_REQUESTS}/minute",
        strategy="fixed-window",
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


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Custom handler for rate limit exceeded with structured logging."""
    client_ip = get_remote_address(request)
    logger.warning(
        "rate_limit_exceeded",
        client_ip=client_ip,
        path=request.url.path,
        method=request.method,
        limit=exc.detail,
    )
    return _rate_limit_exceeded_handler(request, exc)

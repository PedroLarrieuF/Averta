"""FastAPI dependencies: auth, pagination, rate limiting, etc."""
from typing import Annotated, Optional
from fastapi import Depends, Header, HTTPException, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from prisma import Prisma
from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_access_token, TokenPayload
from app.core.exceptions import UnauthorizedError, ForbiddenError
import structlog

logger = structlog.get_logger()

# Security scheme
bearer_scheme = HTTPBearer(auto_error=False)


# Database dependency
async def get_database() -> Prisma:
    return await get_db()


DatabaseDep = Annotated[Prisma, Depends(get_database)]


# Pagination
class PaginationParams:
    def __init__(
        self,
        page: Annotated[int, Query(ge=1, description="Page number")] = 1,
        page_size: Annotated[
            int, Query(ge=1, le=100, description="Items per page")
        ] = 20,
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size
        self.limit = page_size


PaginationDep = Annotated[PaginationParams, Depends()]


# Sorting
class SortParams:
    def __init__(
        self,
        sort_by: Annotated[Optional[str], Query(description="Field to sort by")] = None,
        sort_order: Annotated[
            str, Query(pattern="^(asc|desc)$", description="Sort order")
        ] = "desc",
    ):
        self.sort_by = sort_by
        self.sort_order = sort_order


SortDep = Annotated[SortParams, Depends()]


# Filter params (generic)
class FilterParams:
    def __init__(
        self,
        search: Annotated[Optional[str], Query(description="Search term")] = None,
        status: Annotated[Optional[str], Query(description="Filter by status")] = None,
        date_from: Annotated[
            Optional[str], Query(description="Start date (ISO 8601)")
        ] = None,
        date_to: Annotated[
            Optional[str], Query(description="End date (ISO 8601)")
        ] = None,
    ):
        self.search = search
        self.status = status
        self.date_from = date_from
        self.date_to = date_to


FilterDep = Annotated[FilterParams, Depends()]


# Authentication
async def get_current_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
    db: DatabaseDep,
) -> TokenPayload:
    """Extract and validate current user from JWT token"""
    if not credentials:
        raise UnauthorizedError("Missing authorization header")

    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise UnauthorizedError("Invalid or expired token")

    # Verify user still exists and is active
    user = await db.user.find_unique(where={"id": payload.sub})
    if not user or user.status != "ACTIVE":
        raise UnauthorizedError("User not found or inactive")

    return payload


CurrentUserDep = Annotated[TokenPayload, Depends(get_current_user)]


# Optional auth (for public endpoints that can benefit from user context)
async def get_optional_user(
    credentials: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
    db: DatabaseDep,
) -> Optional[TokenPayload]:
    if not credentials:
        return None
    payload = decode_access_token(credentials.credentials)
    if not payload:
        return None
    user = await db.user.find_unique(where={"id": payload.sub})
    if not user or user.status != "ACTIVE":
        return None
    return payload


OptionalUserDep = Annotated[Optional[TokenPayload], Depends(get_optional_user)]


# Role-based access control
def require_roles(*allowed_roles: str):
    """Dependency factory for role-based access"""
    async def role_checker(current_user: CurrentUserDep) -> TokenPayload:
        if current_user.role not in allowed_roles:
            raise ForbiddenError(
                f"Required role(s): {', '.join(allowed_roles)}"
            )
        return current_user
    return role_checker


# Common role dependencies
RequireAdmin = Annotated[TokenPayload, Depends(require_roles("ADMIN"))]
RequireAuditor = Annotated[TokenPayload, Depends(require_roles("ADMIN", "AUDITOR"))]
RequireManager = Annotated[TokenPayload, Depends(require_roles("ADMIN", "MANAGER"))]
RequireClientAccess = Annotated[TokenPayload, Depends(require_roles("ADMIN", "AUDITOR", "MANAGER", "CLIENT"))]


# Company scope - ensure user can only access their company's data
def get_company_id(current_user: CurrentUserDep) -> str:
    """Get company ID from current user (enforces company isolation)"""
    return current_user.company_id


CompanyIdDep = Annotated[str, Depends(get_company_id)]


# Client scope - for client users, restrict to their client
def get_client_id(current_user: CurrentUserDep) -> Optional[str]:
    """Get client ID from current user (None for non-client roles)"""
    return current_user.client_id


ClientIdDep = Annotated[Optional[str], Depends(get_client_id)]


# Rate limiting (simple in-memory, use Redis for production)
class RateLimiter:
    def __init__(self, requests: int = 100, window: int = 60):
        self.requests = requests
        self.window = window
        self._cache: dict[str, list[float]] = {}

    async def __call__(self, request: Request):
        if settings.ENVIRONMENT == "test":
            return

        client_ip = request.client.host if request.client else "unknown"
        key = f"{request.url.path}:{client_ip}"
        import time
        now = time.time()

        if key not in self._cache:
            self._cache[key] = []

        # Clean old entries
        self._cache[key] = [ts for ts in self._cache[key] if now - ts < self.window]

        if len(self._cache[key]) >= self.requests:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded",
            )

        self._cache[key].append(now)


# Standard rate limiter
rate_limiter = RateLimiter(
    requests=settings.RATE_LIMIT_REQUESTS,
    window=settings.RATE_LIMIT_WINDOW,
)

RateLimitDep = Annotated[None, Depends(rate_limiter)]


# Request ID for tracing
async def get_request_id(
    x_request_id: Annotated[Optional[str], Header(alias="X-Request-ID")] = None,
) -> str:
    return x_request_id or ""


RequestIdDep = Annotated[str, Depends(get_request_id)]
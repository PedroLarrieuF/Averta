"""FastAPI dependencies: auth, pagination, rate limiting, etc."""

from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import TYPE_CHECKING, Annotated

import structlog
from fastapi import Depends, Header, Query, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.core.security import TokenPayload, decode_access_token

if TYPE_CHECKING:
    from prisma import Prisma

logger = structlog.get_logger()

# Security scheme
bearer_scheme = HTTPBearer(auto_error=False)


async def get_database() -> AsyncGenerator["Prisma", None]:
    async for db in get_db():
        yield db


DatabaseDep = Annotated["Prisma", Depends(get_database)]


# Pagination
class PaginationParams:
    def __init__(
        self,
        page: Annotated[int, Query(ge=1, description="Page number")] = 1,
        page_size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
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
        sort_by: Annotated[str | None, Query(description="Field to sort by")] = None,
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
        search: Annotated[str | None, Query(description="Search term")] = None,
        status: Annotated[str | None, Query(description="Filter by status")] = None,
        date_from: Annotated[str | None, Query(description="Start date (ISO 8601)")] = None,
        date_to: Annotated[str | None, Query(description="End date (ISO 8601)")] = None,
    ):
        self.search = search
        self.status = status
        self.date_from = date_from
        self.date_to = date_to


FilterDep = Annotated[FilterParams, Depends()]


# Authentication
async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
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
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: DatabaseDep,
) -> TokenPayload | None:
    if not credentials:
        return None
    payload = decode_access_token(credentials.credentials)
    if not payload:
        return None
    user = await db.user.find_unique(where={"id": payload.sub})
    if not user or user.status != "ACTIVE":
        return None
    return payload


OptionalUserDep = Annotated[TokenPayload | None, Depends(get_optional_user)]


# Role-based access control


def require_roles(*allowed_roles: str) -> Callable[[TokenPayload], Awaitable[TokenPayload]]:
    """Dependency factory for role-based access"""

    async def role_checker(current_user: TokenPayload) -> TokenPayload:
        if current_user.role not in allowed_roles:
            raise ForbiddenError(f"Required role(s): {', '.join(allowed_roles)}")
        return current_user

    return role_checker


# Common role dependencies
RequireAdmin = Annotated[TokenPayload, Depends(require_roles("ADMIN"))]
RequireAuditor = Annotated[TokenPayload, Depends(require_roles("ADMIN", "AUDITOR"))]
RequireManager = Annotated[TokenPayload, Depends(require_roles("ADMIN", "MANAGER"))]
RequireClientAccess = Annotated[
    TokenPayload, Depends(require_roles("ADMIN", "AUDITOR", "MANAGER", "CLIENT"))
]


# Company scope - ensure user can only access their company's data
def get_company_id(current_user: CurrentUserDep) -> str:
    """Get company ID from current user (enforces company isolation)"""
    return current_user.company_id


CompanyIdDep = Annotated[str, Depends(get_company_id)]


# Client scope - for client users, restrict to their client
def get_client_id(current_user: CurrentUserDep) -> str | None:
    """Get client ID from current user (None for non-client roles)"""
    return current_user.client_id


ClientIdDep = Annotated[str | None, Depends(get_client_id)]


# Rate limiting - Redis-backed (slowapi)
# The actual rate limiting is handled by slowapi middleware via limiter.limit() decorator
# This dependency is kept for backward compatibility and can be used to check rate limit status
async def check_rate_limit(request: Request) -> None:
    """
    Rate limit check dependency.
    Actual limiting is done by slowapi decorators on routes.
    This can be used for custom logic if needed.
    """
    # In test environment, skip rate limiting
    if settings.ENVIRONMENT == "test":
        return
    # slowapi handles the actual limiting via decorators
    # This is a placeholder for any custom logic
    pass


RateLimitDep = Annotated[None, Depends(check_rate_limit)]


# Request ID for tracing
async def get_request_id(
    x_request_id: Annotated[str | None, Header(alias="X-Request-ID")] = None,
) -> str:
    return x_request_id or ""


RequestIdDep = Annotated[str, Depends(get_request_id)]

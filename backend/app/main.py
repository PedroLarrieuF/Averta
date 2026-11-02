"""Averta SaaS - FastAPI Application Entry Point"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
import structlog

from app.core.config import settings
from app.core.database import get_prisma, close_prisma
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    prisma_exception_handler,
    jwt_exception_handler,
    generic_exception_handler,
)
from app.core.middleware import (
    RequestIDMiddleware,
    LoggingMiddleware,
    SecurityHeadersMiddleware,
    StructlogMiddleware,
)
from app.core.rate_limit import init_rate_limiter, rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

# Module routers
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.modules.companies.router import router as companies_router
from app.modules.clients.router import router as clients_router
from app.modules.carriers.router import router as carriers_router
from app.modules.branches.router import router as branches_router
from app.modules.contracts.router import router as contracts_router
from app.modules.documents.router import router as documents_router
from app.modules.discrepancies.router import router as discrepancies_router
from app.modules.contests.router import router as contests_router
from app.modules.reports.router import router as reports_router
from app.modules.notifications.router import router as notifications_router
from app.modules.rules.router import router as rules_router
# from app.modules.audit.router import router as audit_router


# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await get_prisma()
    structlog.get_logger().info("application_started", version=settings.APP_VERSION)
    yield
    # Shutdown
    await close_prisma()
    structlog.get_logger().info("application_stopped")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Freight Audit with Success-Based Billing API",
    docs_url=None if settings.ENVIRONMENT == "production" else "/docs",
    redoc_url=None if settings.ENVIRONMENT == "production" else "/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# Middleware (order matters - outermost first)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(StructlogMiddleware)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Initialize rate limiter (must be before exception handlers)
init_rate_limiter(app)

# Exception Handlers
from fastapi.exceptions import RequestValidationError
from prisma.errors import PrismaError
from jose import JWTError

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(PrismaError, prisma_exception_handler)
app.add_exception_handler(JWTError, jwt_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


# Custom Swagger UI (if needed)
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{settings.APP_NAME} - API Docs",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )


@app.get("/redoc", include_in_schema=False)
async def custom_redoc():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{settings.APP_NAME} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )


# Health check (no auth required)
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


# API Routes
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(users_router, prefix=settings.API_PREFIX)
app.include_router(companies_router, prefix=settings.API_PREFIX)
app.include_router(clients_router, prefix=settings.API_PREFIX)
app.include_router(carriers_router, prefix=settings.API_PREFIX)
app.include_router(branches_router, prefix=settings.API_PREFIX)
app.include_router(contracts_router, prefix=settings.API_PREFIX)
app.include_router(documents_router, prefix=settings.API_PREFIX)
app.include_router(discrepancies_router, prefix=settings.API_PREFIX)
app.include_router(contests_router, prefix=settings.API_PREFIX)
app.include_router(reports_router, prefix=settings.API_PREFIX)
app.include_router(notifications_router, prefix=settings.API_PREFIX)
app.include_router(rules_router, prefix=settings.API_PREFIX)
# app.include_router(audit_router, prefix=settings.API_PREFIX)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_config=None,  # Use structlog
    )
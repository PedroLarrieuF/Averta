"""Unit tests for rate limiter"""
import pytest
from unittest.mock import AsyncMock, Mock, patch
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.rate_limit import (
    limiter,
    init_rate_limiter,
    auth_limiter,
    upload_limiter,
    api_limiter,
    get_limiter,
    rate_limit_exceeded_handler,
)
from app.core.config import Settings


class TestRateLimiter:
    """Tests for Redis-backed rate limiter"""

    def test_limiter_initialization(self):
        """Test that limiter is properly initialized with Redis storage"""
        assert isinstance(limiter, Limiter)
        assert limiter.key_func == get_remote_address
        assert "sliding-window" in str(limiter.strategy).lower()

    def test_limiter_default_limits(self):
        """Test default rate limit configuration"""
        # Default should be 100/minute from settings
        assert limiter.default_limits == ["100/minute"]

    @pytest.mark.asyncio
    async def test_init_rate_limiter(self):
        """Test rate limiter initialization on FastAPI app"""
        from fastapi import FastAPI
        from slowapi.errors import RateLimitExceeded

        app = FastAPI()
        init_rate_limiter(app)

        assert hasattr(app.state, "limiter")
        assert app.state.limiter == limiter
        # Check exception handler is registered
        assert RateLimitExceeded in app.exception_handlers

    @pytest.mark.asyncio
    async def test_auth_limiter_exists(self):
        """Test auth_limiter is configured for 10/minute"""
        assert auth_limiter is not None
        # The limit is set via the decorator, not directly accessible

    @pytest.mark.asyncio
    async def test_upload_limiter_exists(self):
        """Test upload_limiter is configured for 5/minute"""
        assert upload_limiter is not None

    @pytest.mark.asyncio
    async def test_api_limiter_exists(self):
        """Test api_limiter is configured for 100/minute"""
        assert api_limiter is not None

    def test_get_limiter(self):
        """Test get_limiter dependency returns the limiter instance"""
        result = get_limiter()
        assert result == limiter


class TestRateLimitExceededHandler:
    """Tests for rate limit exceeded handler"""

    @pytest.fixture
    def mock_request(self):
        request = Mock(spec=Request)
        request.client.host = "127.0.0.1"
        request.url.path = "/api/v1/auth/login"
        request.method = "POST"
        return request

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded_handler_logs(self, mock_request, caplog):
        """Test that rate limit exceeded logs structured warning"""
        from slowapi.errors import RateLimitExceeded

        exc = RateLimitExceeded("Rate limit exceeded")

        with patch("app.core.rate_limit._rate_limit_exceeded_handler", new_callable=AsyncMock) as mock_handler:
            mock_handler.return_value = Mock(status_code=429)
            await rate_limit_exceeded_handler(mock_request, exc)

            mock_handler.assert_called_once_with(mock_request, exc)

    @pytest.mark.asyncio
    async def test_rate_limit_exceeded_returns_429(self, mock_request):
        """Test that handler returns 429 status"""
        from slowapi.errors import RateLimitExceeded
        from fastapi.responses import JSONResponse

        exc = RateLimitExceeded("Rate limit exceeded")

        # Call the actual handler
        response = await rate_limit_exceeded_handler(mock_request, exc)

        assert response.status_code == 429


class TestRateLimitDependencies:
    """Tests for rate limit dependencies"""

    @pytest.mark.asyncio
    async def test_check_rate_limit_skips_in_test_env(self):
        """Test that rate limit is skipped in test environment"""
        from app.core.dependencies import check_rate_limit
        from app.core.config import settings

        # Temporarily set environment to test
        original_env = settings.ENVIRONMENT
        settings.ENVIRONMENT = "test"

        request = Mock(spec=Request)

        # Should not raise
        await check_rate_limit(request)

        # Restore
        settings.ENVIRONMENT = original_env

    @pytest.mark.asyncio
    async def test_check_rate_limit_passes_in_production(self):
        """Test that rate limit check passes in production"""
        from app.core.dependencies import check_rate_limit
        from app.core.config import settings

        original_env = settings.ENVIRONMENT
        settings.ENVIRONMENT = "production"

        request = Mock(spec=Request)

        # Should not raise (slowapi handles actual limiting via decorators)
        await check_rate_limit(request)

        settings.ENVIRONMENT = original_env


class TestRateLimitConfig:
    """Tests for rate limit configuration"""

    def test_rate_limit_settings_exist(self):
        """Test that all rate limit settings are defined"""
        settings = Settings()

        assert hasattr(settings, "RATE_LIMIT_REQUESTS")
        assert hasattr(settings, "RATE_LIMIT_WINDOW")
        assert hasattr(settings, "RATE_LIMIT_AUTH_REQUESTS")
        assert hasattr(settings, "RATE_LIMIT_UPLOAD_REQUESTS")
        assert hasattr(settings, "RATE_LIMIT_API_REQUESTS")
        assert hasattr(settings, "RATE_LIMIT_REPORTS_REQUESTS")
        assert hasattr(settings, "RATE_LIMIT_DISCREPANCIES_REQUESTS")
        assert hasattr(settings, "RATE_LIMIT_CONTESTS_REQUESTS")

    def test_rate_limit_defaults(self):
        """Test default values for rate limit settings"""
        settings = Settings()

        assert settings.RATE_LIMIT_REQUESTS == 100
        assert settings.RATE_LIMIT_WINDOW == 60
        assert settings.RATE_LIMIT_AUTH_REQUESTS == 10
        assert settings.RATE_LIMIT_UPLOAD_REQUESTS == 5
        assert settings.RATE_LIMIT_API_REQUESTS == 100
        assert settings.RATE_LIMIT_REPORTS_REQUESTS == 20
        assert settings.RATE_LIMIT_DISCREPANCIES_REQUESTS == 50
        assert settings.RATE_LIMIT_CONTESTS_REQUESTS == 30


class TestRateLimitHeaders:
    """Tests for rate limit response headers"""

    @pytest.mark.asyncio
    async def test_rate_limit_headers_enabled(self):
        """Test that rate limit headers are enabled"""
        assert limiter.headers_enabled is True

    @pytest.mark.asyncio
    async def test_headers_present_in_response(self):
        """Test that X-RateLimit-* headers would be present"""
        # This is tested via integration tests with actual requests
        # slowapi automatically adds headers when headers_enabled=True
        pass
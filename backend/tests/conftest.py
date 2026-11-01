"""Pytest configuration"""
import pytest
import asyncio
from typing import AsyncGenerator


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def async_client():
    """Async test client fixture."""
    # This would be used with httpx.AsyncClient for API tests
    pass


# Configure pytest-asyncio
pytest_asyncio_mode = "auto"
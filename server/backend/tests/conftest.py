"""Test configuration and fixtures."""

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.fixture
async def client():
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_tunnel_data():
    """Sample tunnel data for testing."""
    return {
        "route": "test-tunnel",
        "description": "Test tunnel for unit tests"
    }
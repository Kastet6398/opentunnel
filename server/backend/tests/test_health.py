"""Tests for health endpoints."""

import pytest


@pytest.mark.asyncio
async def test_root_endpoint(client):
    """Test the root health endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
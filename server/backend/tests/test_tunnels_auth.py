"""Tests for authenticated tunnel endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_tunnel_unauthorized(client: AsyncClient):
    """Test creating tunnel without authentication."""
    tunnel_data = {
        "route": "test-tunnel",
        "description": "Test tunnel"
    }
    
    response = await client.post("/api/tunnels", json=tunnel_data)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_tunnels_unauthorized(client: AsyncClient):
    """Test listing tunnels without authentication."""
    response = await client.get("/api/tunnels")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_tunnel_unauthorized(client: AsyncClient):
    """Test deleting tunnel without authentication."""
    response = await client.delete("/api/tunnels/test-tunnel")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_tunnel_authorized(client: AsyncClient):
    """Test creating tunnel with authentication."""
    user_data = {
        "email": "test@example.com",
        "phone_number": "+1234567890",
        "password": "testpassword123"
    }
    
    # Register and login
    await client.post("/api/auth/register", json=user_data)
    login_response = await client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpassword123"
    })
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    tunnel_data = {
        "route": "test-tunnel",
        "description": "Test tunnel"
    }
    
    response = await client.post("/api/tunnels", json=tunnel_data, headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["route"] == tunnel_data["route"]
    assert "token" in data
    assert "public_url" in data
    assert "ws_url" in data


@pytest.mark.asyncio
async def test_list_tunnels_authorized(client: AsyncClient):
    """Test listing tunnels with authentication."""
    user_data = {
        "email": "test@example.com",
        "phone_number": "+1234567890",
        "password": "testpassword123"
    }
    
    # Register and login
    await client.post("/api/auth/register", json=user_data)
    login_response = await client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpassword123"
    })
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    response = await client.get("/api/tunnels", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "tunnels" in data
    assert isinstance(data["tunnels"], list)


@pytest.mark.asyncio
async def test_delete_tunnel_authorized(client: AsyncClient):
    """Test deleting tunnel with authentication."""
    user_data = {
        "email": "test@example.com",
        "phone_number": "+1234567890",
        "password": "testpassword123"
    }
    
    # Register and login
    await client.post("/api/auth/register", json=user_data)
    login_response = await client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpassword123"
    })
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # First create a tunnel
    tunnel_data = {
        "route": "test-tunnel",
        "description": "Test tunnel"
    }
    await client.post("/api/tunnels", json=tunnel_data, headers=headers)
    
    # Then delete it
    response = await client.delete("/api/tunnels/test-tunnel", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["route"] == "test-tunnel"
    assert data["removed"] is True
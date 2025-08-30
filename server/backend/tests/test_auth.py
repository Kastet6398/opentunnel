"""Tests for authentication endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration."""
    user_data = {
        "email": "test@example.com",
        "phone_number": "+1234567890",
        "password": "testpassword123"
    }
    
    response = await client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["phone_number"] == user_data["phone_number"]
    assert "id" in data
    assert "password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test registration with duplicate email."""
    user_data = {
        "email": "test@example.com",
        "phone_number": "+1234567890",
        "password": "testpassword123"
    }
    
    # First registration should succeed
    response = await client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201
    
    # Second registration with same email should fail
    user_data["phone_number"] = "+0987654321"
    response = await client.post("/api/auth/register", json=user_data)
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_duplicate_phone(client: AsyncClient):
    """Test registration with duplicate phone number."""
    user_data = {
        "email": "test@example.com",
        "phone_number": "+1234567890",
        "password": "testpassword123"
    }
    
    # First registration should succeed
    response = await client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201
    
    # Second registration with same phone should fail
    user_data["email"] = "test2@example.com"
    response = await client.post("/api/auth/register", json=user_data)
    assert response.status_code == 400
    assert "Phone number already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test successful login."""
    user_data = {
        "email": "test@example.com",
        "phone_number": "+1234567890",
        "password": "testpassword123"
    }
    
    # Register user
    await client.post("/api/auth/register", json=user_data)
    
    # Login
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    }
    
    response = await client.post("/api/auth/login", json=login_data)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient):
    """Test getting current user information."""
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
    
    response = await client.get("/api/auth/me", headers=headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["phone_number"] == user_data["phone_number"]


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: AsyncClient):
    """Test getting current user without authentication."""
    response = await client.get("/api/auth/me")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    """Test token refresh."""
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
    
    refresh_token = login_response.json()["refresh_token"]
    
    response = await client.post("/api/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    """Test logout."""
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
    
    refresh_token = login_response.json()["refresh_token"]
    
    response = await client.post("/api/auth/logout", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200
    assert "Successfully logged out" in response.json()["message"]
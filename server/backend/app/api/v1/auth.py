"""Authentication API endpoints."""

import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.config import settings
from ...core.database import get_db
from ...models.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from ...models.database import User
from ...services.auth_service import AuthService
from ...utils.exceptions import create_auth_error_detail
from ..dependencies import get_auth_service, get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_create: UserCreate,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserResponse:
    """Register a new user."""
    try:
        user = await auth_service.create_user(db, user_create)
        logger.info("User registered: %s", user.email)
        return UserResponse.from_orm(user)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Registration error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=[create_auth_error_detail(
                error_type="server_error",
                location=["body"],
                message="Registration failed",
                input_value=None,
                context={"error": str(e)}
            )]
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_request: LoginRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """Login with email and password."""
    user = await auth_service.authenticate_user(db, login_request.email, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=[create_auth_error_detail(
                error_type="authentication_error",
                location=["body", "email", "password"],
                message="Incorrect email or password",
                input_value={"email": login_request.email},
                context={"error": "Invalid credentials"}
            )],
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[create_auth_error_detail(
                error_type="value_error",
                location=["body"],
                message="Inactive user",
                input_value={"email": login_request.email},
                context={"error": "User account is deactivated"}
            )]
        )
    
    # Create tokens
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    
    refresh_token = auth_service.create_refresh_token(
        data={"sub": str(user.id), "email": user.email}
    )
    
    # Store refresh token
    await auth_service.store_refresh_token(db, user.id, refresh_token)
    
    # Update last login
    await auth_service.update_last_login(db, user.id)
    
    logger.info("User logged in: %s", user.email)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    """Refresh access token using refresh token."""
    user = await auth_service.verify_refresh_token(db, refresh_request.refresh_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=[create_auth_error_detail(
                error_type="authentication_error",
                location=["body", "refresh_token"],
                message="Invalid refresh token",
                input_value=refresh_request.refresh_token,
                context={"error": "Token is invalid or expired"}
            )],
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[create_auth_error_detail(
                error_type="value_error",
                location=["body"],
                message="Inactive user",
                input_value={"refresh_token": refresh_request.refresh_token},
                context={"error": "User account is deactivated"}
            )]
        )
    
    # Create new access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    
    # Create new refresh token
    new_refresh_token = auth_service.create_refresh_token(
        data={"sub": str(user.id), "email": user.email}
    )
    
    # Revoke old refresh token and store new one
    await auth_service.revoke_refresh_token(db, refresh_request.refresh_token)
    await auth_service.store_refresh_token(db, user.id, new_refresh_token)
    
    logger.info("Token refreshed for user: %s", user.email)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/logout")
async def logout(
    refresh_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    """Logout by revoking refresh token."""
    success = await auth_service.revoke_refresh_token(db, refresh_request.refresh_token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[create_auth_error_detail(
                error_type="value_error",
                location=["body", "refresh_token"],
                message="Invalid refresh token",
                input_value=refresh_request.refresh_token,
                context={"error": "Token not found or already revoked"}
            )]
        )
    
    logger.info("User logged out")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """Get current user information."""
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserResponse:
    """Update current user information."""
    updated_user = await auth_service.update_user(db, current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[create_auth_error_detail(
                error_type="not_found_error",
                location=["path", "user_id"],
                message="User not found",
                input_value=current_user.id,
                context={"error": "User does not exist"}
            )]
        )
    
    logger.info("User updated: %s", updated_user.email)
    return UserResponse.from_orm(updated_user)


@router.post("/change-password")
async def change_password(
    password_request: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(get_auth_service)
) -> dict:
    """Change user password."""
    # Verify current password
    if not auth_service.verify_password(password_request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[create_auth_error_detail(
                error_type="authentication_error",
                location=["body", "current_password"],
                message="Incorrect current password",
                input_value=None,  # Don't expose password in response
                context={"error": "Password verification failed"}
            )]
        )
    
    # Update password
    user_update = UserUpdate(password=password_request.new_password)
    await auth_service.update_user(db, current_user.id, user_update)
    
    logger.info("Password changed for user: %s", current_user.email)
    return {"message": "Password changed successfully"}
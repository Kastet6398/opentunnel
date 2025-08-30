"""API dependencies."""

from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..models.database import User
from ..services.auth_service import AuthService
from ..utils.exceptions import create_auth_error_detail

# Security scheme
security = HTTPBearer()

# Global auth service instance
auth_service = AuthService()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get the current authenticated user."""
    token = credentials.credentials
    token_data = auth_service.verify_token(token)
    
    user = await auth_service.get_user_by_id(db, user_id=token_data.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=[create_auth_error_detail(
                error_type="authentication_error",
                location=["header", "authorization"],
                message="User not found",
                input_value=token,
                context={"error": "User associated with token does not exist"}
            )],
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[create_auth_error_detail(
                error_type="value_error",
                location=["header", "authorization"],
                message="Inactive user",
                input_value=token,
                context={"error": "User account is deactivated"}
            )]
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get the current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[create_auth_error_detail(
                error_type="value_error",
                location=["header", "authorization"],
                message="Inactive user",
                input_value=None,
                context={"error": "User account is deactivated"}
            )]
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Get the current verified user."""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=[create_auth_error_detail(
                error_type="value_error",
                location=["header", "authorization"],
                message="User not verified",
                input_value=None,
                context={"error": "User account is not verified"}
            )]
        )
    return current_user


def get_auth_service() -> AuthService:
    """Get authentication service."""
    return auth_service
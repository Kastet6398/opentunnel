"""Authentication-related data models."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, validator
import phonenumbers


class UserBase(BaseModel):
    """Base user model."""
    
    email: EmailStr = Field(..., description="User email address")
    phone_number: str = Field(..., description="User phone number")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format."""
        try:
            parsed = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError('Invalid phone number')
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise ValueError('Invalid phone number format')


class UserCreate(UserBase):
    """User creation model."""
    
    password: str = Field(..., min_length=8, max_length=128, description="User password")


class UserUpdate(BaseModel):
    """User update model."""
    
    email: Optional[EmailStr] = Field(None, description="User email address")
    phone_number: Optional[str] = Field(None, description="User phone number")
    password: Optional[str] = Field(None, min_length=8, max_length=128, description="User password")
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        """Validate phone number format."""
        if v is None:
            return v
        try:
            parsed = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError('Invalid phone number')
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except phonenumbers.NumberParseException:
            raise ValueError('Invalid phone number format')


class UserResponse(UserBase):
    """User response model."""
    
    id: int = Field(..., description="User ID")
    is_active: bool = Field(..., description="Whether user is active")
    is_verified: bool = Field(..., description="Whether user is verified")
    created_at: datetime = Field(..., description="User creation timestamp")
    updated_at: datetime = Field(..., description="User last update timestamp")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    
    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    """Login request model."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class TokenResponse(BaseModel):
    """Token response model."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class RefreshTokenRequest(BaseModel):
    """Refresh token request model."""
    
    refresh_token: str = Field(..., description="Refresh token")


class PasswordResetRequest(BaseModel):
    """Password reset request model."""
    
    email: EmailStr = Field(..., description="User email address")


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation model."""
    
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")


class ChangePasswordRequest(BaseModel):
    """Change password request model."""
    
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")


class TokenData(BaseModel):
    """Token data model."""
    
    user_id: Optional[int] = None
    email: Optional[str] = None
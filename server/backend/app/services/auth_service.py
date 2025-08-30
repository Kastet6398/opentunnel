"""Authentication service."""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..models.auth import TokenData, UserCreate, UserUpdate
from ..models.database import RefreshToken, User
from ..utils.exceptions import create_auth_error_detail

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication service for user management and JWT handling."""
    
    def __init__(self):
        self.secret_key = settings.secret_key
        self.algorithm = settings.algorithm
        self.access_token_expire_minutes = settings.access_token_expire_minutes
        self.refresh_token_expire_days = settings.refresh_token_expire_days

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: dict) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str, token_type: str = "access") -> TokenData:
        """Verify and decode a JWT token."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=[create_auth_error_detail(
                error_type="authentication_error",
                location=["header", "authorization"],
                message="Could not validate credentials",
                input_value=token,
                context={"error": "Invalid or expired token"}
            )],
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id: int = payload.get("sub")
            email: str = payload.get("email")
            token_type_claim: str = payload.get("type")
            
            if user_id is None or email is None or token_type_claim != token_type:
                raise credentials_exception
            
            return TokenData(user_id=user_id, email=email)
        except JWTError:
            raise credentials_exception

    async def authenticate_user(self, db: AsyncSession, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password."""
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    async def create_user(self, db: AsyncSession, user_create: UserCreate) -> User:
        """Create a new user."""
        # Check if user already exists
        result = await db.execute(select(User).where(User.email == user_create.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=[create_auth_error_detail(
                    error_type="value_error",
                    location=["body", "email"],
                    message="Email already registered",
                    input_value=user_create.email,
                    context={"error": "Email already exists"}
                )]
            )
        
        result = await db.execute(select(User).where(User.phone_number == user_create.phone_number))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=[create_auth_error_detail(
                    error_type="value_error",
                    location=["body", "phone_number"],
                    message="Phone number already registered",
                    input_value=user_create.phone_number,
                    context={"error": "Phone number already exists"}
                )]
            )
        
        # Create new user
        hashed_password = self.get_password_hash(user_create.password)
        db_user = User(
            email=user_create.email,
            phone_number=user_create.phone_number,
            hashed_password=hashed_password
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def update_user(self, db: AsyncSession, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update user information."""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Check for email conflicts
        if user_update.email and user_update.email != user.email:
            result = await db.execute(select(User).where(User.email == user_update.email))
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=[create_auth_error_detail(
                        error_type="value_error",
                        location=["body", "email"],
                        message="Email already registered",
                        input_value=user_update.email,
                        context={"error": "Email already exists"}
                    )]
                )
        
        # Check for phone number conflicts
        if user_update.phone_number and user_update.phone_number != user.phone_number:
            result = await db.execute(select(User).where(User.phone_number == user_update.phone_number))
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=[create_auth_error_detail(
                        error_type="value_error",
                        location=["body", "phone_number"],
                        message="Phone number already registered",
                        input_value=user_update.phone_number,
                        context={"error": "Phone number already exists"}
                    )]
                )
        
        # Update fields
        if user_update.email:
            user.email = user_update.email
        if user_update.phone_number:
            user.phone_number = user_update.phone_number
        if user_update.password:
            user.hashed_password = self.get_password_hash(user_update.password)
        
        user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(user)
        return user

    async def store_refresh_token(self, db: AsyncSession, user_id: int, token: str) -> RefreshToken:
        """Store a refresh token in the database."""
        expires_at = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        
        db.add(refresh_token)
        await db.commit()
        await db.refresh(refresh_token)
        return refresh_token

    async def revoke_refresh_token(self, db: AsyncSession, token: str) -> bool:
        """Revoke a refresh token."""
        result = await db.execute(select(RefreshToken).where(RefreshToken.token == token))
        refresh_token = result.scalar_one_or_none()
        
        if not refresh_token:
            return False
        
        refresh_token.is_revoked = True
        await db.commit()
        return True

    async def verify_refresh_token(self, db: AsyncSession, token: str) -> Optional[User]:
        """Verify a refresh token and return the associated user."""
        # First verify the JWT
        token_data = self.verify_token(token, "refresh")
        
        # Check if token exists in database and is not revoked
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token == token,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.utcnow()
            )
        )
        refresh_token = result.scalar_one_or_none()
        
        if not refresh_token:
            return None
        
        # Get the user
        return await self.get_user_by_id(db, token_data.user_id)

    async def update_last_login(self, db: AsyncSession, user_id: int) -> None:
        """Update user's last login timestamp."""
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if user:
            user.last_login = datetime.utcnow()
            await db.commit()
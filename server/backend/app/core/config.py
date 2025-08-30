"""Configuration management for the application."""

import os
from typing import Dict, List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # API Configuration
    api_base_url: str = Field(default="http://localhost:8000", env="API_BASE_URL")
    ws_base_url: str = Field(default="ws://localhost:8000", env="WS_BASE_URL")
    public_base_url: str = Field(default="", env="PUBLIC_BASE_URL")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # CORS Configuration
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(default=["*"], env="CORS_ALLOW_METHODS")
    cors_allow_headers: List[str] = Field(default=["*"], env="CORS_ALLOW_HEADERS")
    
    # Tunnel Configuration
    tunnel_timeout: float = Field(default=30.0, env="TUNNEL_TIMEOUT")
    ping_interval: float = Field(default=10.0, env="PING_INTERVAL")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Authentication Configuration
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    
    # Database Configuration
    database_url: str = Field(default="sqlite+aiosqlite:///./routetunnel.db", env="DATABASE_URL")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def get_base_urls(self) -> Dict[str, str]:
        """Get base URLs for different services."""
        public_base = self.public_base_url or self.api_base_url
        return {
            "api": self.api_base_url.rstrip("/"),
            "ws": self.ws_base_url.rstrip("/"),
            "public": public_base.rstrip("/")
        }


# Global settings instance
settings = Settings()

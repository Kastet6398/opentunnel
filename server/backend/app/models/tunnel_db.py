"""Database models for tunnels."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, ForeignKey
from sqlalchemy.sql import func

from .database import Base


class TunnelToken(Base):
    """Tunnel token model for persistent storage."""

    __tablename__ = "tunnel_tokens"

    id = Column(Integer, primary_key=True, index=True)
    route = Column(String(64), unique=True, index=True, nullable=False)
    token = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    is_public = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_connected_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

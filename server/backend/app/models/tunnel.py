"""Tunnel-related data models."""

from pydantic import BaseModel, Field
from typing import List, Optional


class CreateTunnelRequest(BaseModel):
    """Request model for creating a new tunnel."""

    route: str = Field(
        ...,
        min_length=3,
        max_length=64,
        pattern=r"^[a-zA-Z0-9-_]+$",
        description="Unique route identifier for the tunnel"
    )
    description: Optional[str] = Field(
        None,
        max_length=255,
        description="Optional description for the tunnel"
    )
    is_public: bool = Field(
        default=False,
        description="Whether the tunnel should be publicly visible"
    )


class CreateTunnelResponse(BaseModel):
    """Response model for tunnel creation."""
    
    route: str = Field(..., description="The created tunnel route")
    token: str = Field(..., description="Authentication token for the tunnel")
    public_url: str = Field(..., description="Public URL for accessing the tunnel")
    ws_url: str = Field(..., description="WebSocket URL for tunnel connection")


class TunnelInfo(BaseModel):
    """Information about a tunnel."""

    route: str = Field(..., description="Tunnel route identifier")
    connected: bool = Field(..., description="Whether the tunnel is currently connected")
    created_at: float = Field(..., description="Unix timestamp when tunnel was created")
    last_seen: Optional[float] = Field(
        None,
        description="Unix timestamp of last activity"
    )
    description: Optional[str] = Field(
        None,
        description="Optional tunnel description"
    )
    is_public: bool = Field(..., description="Whether the tunnel is publicly visible")


class ListTunnelsResponse(BaseModel):
    """Response model for listing tunnels."""
    
    tunnels: List[TunnelInfo] = Field(..., description="List of tunnel information")


class DeleteTunnelResponse(BaseModel):
    """Response model for tunnel deletion."""
    
    route: str = Field(..., description="The deleted tunnel route")
    removed: bool = Field(..., description="Whether the tunnel was successfully removed")
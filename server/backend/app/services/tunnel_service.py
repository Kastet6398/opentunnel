"""Tunnel service for business logic operations."""

import base64
import logging
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..models.tunnel import (
    CreateTunnelRequest,
    CreateTunnelResponse,
    DeleteTunnelResponse,
    ListTunnelsResponse,
    TunnelInfo,
)
from .registry import TunnelRegistry
from .tunnel_db_service import TunnelDBService

logger = logging.getLogger(__name__)


class TunnelService:
    """Service for tunnel-related business logic."""
    
    def __init__(self, registry: TunnelRegistry, session: AsyncSession):
        self.registry = registry
        self.db_service = TunnelDBService(session)

    async def create_tunnel(self, request: CreateTunnelRequest, user_id: int) -> CreateTunnelResponse:
        """Create a new tunnel."""
        # Check if route already exists before creating anything
        if await self.db_service.get_tunnel_token(request.route):
            raise HTTPException(status_code=409, detail="Route already exists")

        # Create tunnel in registry only after we've confirmed route is available
        tunnel = await self.registry.create_tunnel(
            route=request.route,
            description=request.description
        )

        # Store token in database
        await self.db_service.create_tunnel_token(
            route=tunnel.route,
            token=tunnel.token,
            description=request.description,
            user_id=user_id,
            is_public=request.is_public
        )

        logger.info("Created tunnel route=%s", request.route)

        urls = settings.get_base_urls()
        return CreateTunnelResponse(
            route=tunnel.route,
            token=tunnel.token,
            public_url=f"{urls['public']}/r/{tunnel.route}",
            ws_url=f"{urls['ws']}/ws/tunnel?token={tunnel.token}",
        )

    async def list_tunnels(self, user_id: int) -> ListTunnelsResponse:
        """List all tunnels for a specific user.

        Previously this returned only tunnels present in the in-memory registry which
        made /api/tunnels empty when the registry had no entries (e.g. after restart).
        Instead, fetch all active tokens from the database and merge runtime state
        from the registry (connected/last_seen) when available.
        """
        # Get all user's tokens from the database
        user_tokens = await self.db_service.get_user_tunnel_tokens(user_id)

        tunnels = []
        for db_token in user_tokens:
            # Try to get runtime info from registry
            reg_tunnel = await self.registry.get_tunnel(db_token.route)

            if reg_tunnel:
                created_at = reg_tunnel.created_at
                last_seen = reg_tunnel.last_seen
                connected = reg_tunnel.connected
                description = reg_tunnel.description if reg_tunnel.description is not None else db_token.description
            else:
                # Convert DB datetimes to unix timestamps expected by TunnelInfo
                created_at = db_token.created_at.timestamp() if hasattr(db_token, 'created_at') and db_token.created_at is not None else 0
                last_seen = db_token.last_connected_at.timestamp() if hasattr(db_token, 'last_connected_at') and db_token.last_connected_at is not None else None
                connected = False
                description = db_token.description

            tunnels.append(
                TunnelInfo(
                    route=db_token.route,
                    connected=connected,
                    created_at=created_at,
                    last_seen=last_seen,
                    description=description,
                    is_public=db_token.is_public,
                )
            )

        return ListTunnelsResponse(tunnels=tunnels)

    async def list_public_tunnels(self) -> ListTunnelsResponse:
        """List all public tunnels."""
        # Get all public tokens from the database
        public_tokens = await self.db_service.get_public_tunnel_tokens()

        tunnels = []
        for db_token in public_tokens:
            # Try to get runtime info from registry
            reg_tunnel = await self.registry.get_tunnel(db_token.route)

            if reg_tunnel:
                created_at = reg_tunnel.created_at
                last_seen = reg_tunnel.last_seen
                connected = reg_tunnel.connected
                description = reg_tunnel.description if reg_tunnel.description is not None else db_token.description
            else:
                # Convert DB datetimes to unix timestamps expected by TunnelInfo
                created_at = db_token.created_at.timestamp() if hasattr(db_token, 'created_at') and db_token.created_at is not None else 0
                last_seen = db_token.last_connected_at.timestamp() if hasattr(db_token, 'last_connected_at') and db_token.last_connected_at is not None else None
                connected = False
                description = db_token.description

            tunnels.append(
                TunnelInfo(
                    route=db_token.route,
                    connected=connected,
                    created_at=created_at,
                    last_seen=last_seen,
                    description=description,
                    is_public=True,  # All tunnels in this list are public
                )
            )

        return ListTunnelsResponse(tunnels=tunnels)

    async def delete_tunnel(self, route: str) -> DeleteTunnelResponse:
        """Delete a tunnel."""
        # Delete from registry
        removed = await self.registry.delete_tunnel(route)
        if not removed:
            raise HTTPException(status_code=404, detail="Not found")
        
        # Delete from database
        await self.db_service.delete_tunnel_token(route)
        
        logger.info("Deleted tunnel route=%s", route)
        return DeleteTunnelResponse(route=route, removed=True)

    async def forward_request(
        self, 
        request: Request, 
        route: str, 
        rest_of_path: str = ""
    ) -> Response:
        """Forward a request through a tunnel."""
        body_bytes = await request.body()
        headers = {
            k.decode().lower() if isinstance(k, bytes) else k.lower(): 
            (v.decode() if isinstance(v, bytes) else v) 
            for k, v in request.headers.items()
        }
        
        query_params: Dict[str, List[str]] = {}
        for key, value in request.query_params.multi_items():
            query_params.setdefault(key, []).append(value)
        
        payload: Dict[str, any] = {
            "correlation_id": "",
            "method": request.method,
            "path": f"/{rest_of_path}" if rest_of_path else "/",
            "query": query_params,
            "headers": headers,
            "body_b64": base64.b64encode(body_bytes).decode("ascii") if body_bytes else None,
        }
        
        try:
            resp: Dict[str, any] = await self.registry.send_ingress_request(
                route=route, 
                payload=payload,
                timeout=settings.tunnel_timeout
            )
        except ConnectionError:
            logger.info("Ingress route=%s no connection", route)
            raise HTTPException(status_code=502, detail="Tunnel not connected")
        
        status_code = int(resp.get("status_code", 502))
        resp_headers: Dict[str, str] = resp.get("headers", {}) or {}
        body_b64: Optional[str] = resp.get("body_b64")
        body = base64.b64decode(body_b64.encode("ascii")) if body_b64 else b""
        
        return Response(content=body, status_code=status_code, headers=resp_headers)
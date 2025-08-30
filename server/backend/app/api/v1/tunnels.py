"""Tunnel API endpoints."""

import logging
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect

from ...core.config import settings
from ...models.tunnel import (
    CreateTunnelRequest,
    CreateTunnelResponse,
    DeleteTunnelResponse,
    ListTunnelsResponse,
)
from ...models.database import User
from ...services import TunnelRegistry, TunnelService
from ..dependencies import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tunnels", tags=["tunnels"])


def get_tunnel_service() -> TunnelService:
    """Dependency to get tunnel service."""
    # This will be injected by the main app
    return get_tunnel_service._service


def get_tunnel_registry() -> TunnelRegistry:
    """Dependency to get tunnel registry."""
    # This will be injected by the main app
    return get_tunnel_registry._registry


@router.post("", response_model=CreateTunnelResponse)
async def create_tunnel(
    payload: CreateTunnelRequest,
    current_user: User = Depends(get_current_active_user),
    service: TunnelService = Depends(get_tunnel_service)
) -> CreateTunnelResponse:
    """Create a new tunnel."""
    return await service.create_tunnel(payload, current_user.id)


@router.get("", response_model=ListTunnelsResponse)
async def list_tunnels(
    current_user: User = Depends(get_current_active_user),
    service: TunnelService = Depends(get_tunnel_service)
) -> ListTunnelsResponse:
    """List all tunnels for the current user."""
    return await service.list_tunnels(current_user.id)


@router.get("/public", response_model=ListTunnelsResponse)
async def list_public_tunnels(
    service: TunnelService = Depends(get_tunnel_service)
) -> ListTunnelsResponse:
    """List all public tunnels."""
    return await service.list_public_tunnels()


@router.delete("/{route}", response_model=DeleteTunnelResponse)
async def delete_tunnel(
    route: str,
    current_user: User = Depends(get_current_active_user),
    service: TunnelService = Depends(get_tunnel_service)
) -> DeleteTunnelResponse:
    """Delete a tunnel."""
    return await service.delete_tunnel(route)


@router.websocket("/ws/tunnel")
async def tunnel_ws(
    websocket: WebSocket,
    registry: TunnelRegistry = Depends(get_tunnel_registry)
) -> None:
    """WebSocket endpoint for tunnel connections."""
    token = websocket.query_params.get("token")
    if not token:
        logger.warning("WebSocket attach rejected: missing token")
        await websocket.close(code=4401)
        return
    
    # Validate token before accepting connection
    async with registry._lock:
        route = registry._token_to_route.get(token)
        if not route:
            logger.warning("WebSocket attach rejected: invalid token")
            await websocket.close(code=4403)
            return
        
        tunnel = registry._route_to_tunnel.get(route)
        if not tunnel:
            logger.warning("WebSocket attach rejected: invalid route")
            await websocket.close(code=4404)
            return
    
    await websocket.accept()
    tunnel = await registry.attach_websocket(token=token, websocket=websocket)
    logger.info("WebSocket attached route=%s", tunnel.route)
    
    try:
        while True:
            message = await websocket.receive_json()
            await registry.handle_client_message(websocket, message)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
        await registry.detach_websocket(websocket)
    except Exception as exc:
        logger.warning("WebSocket error: %s", exc)
        await registry.detach_websocket(websocket)
        try:
            await websocket.close()
        except Exception:
            pass
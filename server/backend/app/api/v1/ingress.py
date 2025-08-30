"""Ingress API endpoints for public tunnel access."""

import logging
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, Request

from ...services import TunnelService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ingress"])


def get_tunnel_service() -> TunnelService:
    """Dependency to get tunnel service."""
    # This will be injected by the main app
    return get_tunnel_service._service


@router.api_route("/r/{route}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def route_root(
    request: Request, 
    route: str,
    service: TunnelService = Depends(get_tunnel_service)
):
    """Handle requests to tunnel root path."""
    return await service.forward_request(request, route=route, rest_of_path="")


@router.api_route("/r/{route}/{rest_of_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"])
async def route_rest(
    request: Request, 
    route: str, 
    rest_of_path: str,
    service: TunnelService = Depends(get_tunnel_service)
):
    """Handle requests to tunnel sub-paths."""
    return await service.forward_request(request, route=route, rest_of_path=rest_of_path)
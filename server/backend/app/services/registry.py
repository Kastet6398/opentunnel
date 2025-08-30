"""Tunnel registry service for managing tunnel connections."""

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, TYPE_CHECKING

from starlette.websockets import WebSocket

if TYPE_CHECKING:
    from .tunnel_db_service import TunnelDBService


@dataclass
class PendingRequest:
    """Represents a pending request waiting for response."""
    
    future: asyncio.Future
    created_at: float


@dataclass
class Tunnel:
    """Represents a tunnel connection."""
    
    route: str
    token: str
    description: Optional[str] = None
    created_at: float = field(default_factory=lambda: time.time())
    last_seen: Optional[float] = None
    websocket: Optional[WebSocket] = None
    connected: bool = False
    pending: Dict[str, PendingRequest] = field(default_factory=dict)


class TunnelRegistry:
    """Registry for managing tunnel connections and routing."""
    
    def __init__(self, db_service: Optional['TunnelDBService'] = None) -> None:
        self._route_to_tunnel: Dict[str, Tunnel] = {}
        self._token_to_route: Dict[str, str] = {}
        self._lock = asyncio.Lock()
        self._db_service = db_service

    async def create_tunnel(self, route: str, description: Optional[str] = None) -> Tunnel:
        """Create a new tunnel."""
        async with self._lock:
            if route in self._route_to_tunnel:
                raise ValueError("Route already exists")
            
            token = uuid.uuid4().hex
            tunnel = Tunnel(route=route, token=token, description=description)
            self._route_to_tunnel[route] = tunnel
            self._token_to_route[token] = route
            return tunnel

    async def get_tunnel(self, route: str) -> Optional[Tunnel]:
        """Get tunnel by route."""
        async with self._lock:
            return self._route_to_tunnel.get(route)

    async def list_tunnels(self) -> Dict[str, Tunnel]:
        """List all tunnels."""
        async with self._lock:
            return dict(self._route_to_tunnel)

    async def delete_tunnel(self, route: str) -> bool:
        """Delete a tunnel."""
        async with self._lock:
            tunnel = self._route_to_tunnel.pop(route, None)
            if not tunnel:
                return False
            
            if tunnel.token in self._token_to_route:
                self._token_to_route.pop(tunnel.token, None)
            
            # Close websocket if connected
            try:
                if tunnel.websocket:
                    await tunnel.websocket.close()
            except Exception:
                pass
            
            return True

    async def attach_websocket(self, token: str, websocket: WebSocket) -> Tunnel:
        """Attach a websocket to a tunnel."""
        # First validate token in database if DB service is available
        if self._db_service:
            db_token = await self._db_service.validate_token(token)
            if not db_token or not db_token.is_active:
                raise PermissionError("Invalid token")
            
            # Update last connected timestamp
            await self._db_service.update_last_connected(db_token.route)
        
        async with self._lock:
            route = self._token_to_route.get(token)
            if not route:
                raise PermissionError("Invalid token")
            
            tunnel = self._route_to_tunnel.get(route)
            if not tunnel:
                raise PermissionError("Unknown route")
            
            tunnel.websocket = websocket
            tunnel.connected = True
            tunnel.last_seen = time.time()
            return tunnel

    async def detach_websocket(self, websocket: WebSocket) -> None:
        """Detach a websocket from its tunnel."""
        async with self._lock:
            for tunnel in self._route_to_tunnel.values():
                if tunnel.websocket is websocket:
                    tunnel.websocket = None
                    tunnel.connected = False
                    tunnel.last_seen = time.time()
                    break

    async def send_ingress_request(
        self, 
        route: str, 
        payload: Dict[str, Any], 
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """Send an ingress request through a tunnel."""
        async with self._lock:
            tunnel = self._route_to_tunnel.get(route)
            if not tunnel or not tunnel.connected or not tunnel.websocket:
                raise ConnectionError("Tunnel not connected")
            
            websocket = tunnel.websocket
            correlation_id = payload.get("correlation_id")
            if not correlation_id:
                correlation_id = uuid.uuid4().hex
                payload["correlation_id"] = correlation_id
            
            loop = asyncio.get_running_loop()
            future: asyncio.Future = loop.create_future()
            tunnel.pending[correlation_id] = PendingRequest(
                future=future, 
                created_at=time.time()
            )

        await websocket.send_json({"type": "request", **payload})

        try:
            response: Dict[str, Any] = await asyncio.wait_for(future, timeout=timeout)
            return response
        finally:
            async with self._lock:
                tunnel = self._route_to_tunnel.get(route)
                if tunnel:
                    tunnel.pending.pop(correlation_id, None)

    async def handle_client_message(self, websocket: WebSocket, message: Dict[str, Any]) -> None:
        """Handle messages from tunnel clients."""
        msg_type = message.get("type")
        
        if msg_type == "pong":
            async with self._lock:
                for tunnel in self._route_to_tunnel.values():
                    if tunnel.websocket is websocket:
                        tunnel.last_seen = time.time()
                        break
            return
        
        if msg_type != "response":
            return
        
        correlation_id: Optional[str] = message.get("correlation_id")
        if not correlation_id:
            return
        
        async with self._lock:
            for tunnel in self._route_to_tunnel.values():
                if tunnel.websocket is websocket:
                    pending = tunnel.pending.get(correlation_id)
                    if pending and not pending.future.done():
                        pending.future.set_result(message)
                    break

    async def ping_connected(self) -> None:
        """Ping all connected tunnels."""
        async with self._lock:
            tunnels = [
                t for t in self._route_to_tunnel.values() 
                if t.connected and t.websocket
            ]
        
        for tunnel in tunnels:
            try:
                await tunnel.websocket.send_json({"type": "ping", "ts": time.time()})
            except Exception:
                async with self._lock:
                    if tunnel.websocket:
                        try:
                            await tunnel.websocket.close()
                        except Exception:
                            pass
                    tunnel.websocket = None
                    tunnel.connected = False
                    tunnel.last_seen = time.time()
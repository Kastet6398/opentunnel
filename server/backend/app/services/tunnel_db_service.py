"""Database service for tunnel operations."""

from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.tunnel_db import TunnelToken


class TunnelDBService:
    """Service for tunnel database operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_tunnel_token(
        self,
        route: str,
        token: str,
        description: Optional[str],
        user_id: int,
        is_public: bool = False
    ) -> TunnelToken:
        """Create a new tunnel token record."""
        tunnel_token = TunnelToken(
            route=route,
            token=token,
            description=description,
            user_id=user_id,
            is_public=is_public
        )
        self.session.add(tunnel_token)
        await self.session.commit()
        await self.session.refresh(tunnel_token)
        return tunnel_token

    async def get_tunnel_token(self, route: str) -> Optional[TunnelToken]:
        """Get a tunnel token by route."""
        result = await self.session.execute(
            select(TunnelToken).where(TunnelToken.route == route)
        )
        return result.scalars().first()

    async def delete_tunnel_token(self, route: str) -> bool:
        """Delete a tunnel token."""
        token = await self.get_tunnel_token(route)
        if token:
            await self.session.delete(token)
            await self.session.commit()
            return True
        return False

    async def update_last_connected(self, route: str) -> None:
        """Update last connected timestamp for a tunnel."""
        token = await self.get_tunnel_token(route)
        if token:
            token.last_connected_at = datetime.utcnow()
            await self.session.commit()

    async def validate_token(self, token: str) -> Optional[TunnelToken]:
        """Validate a tunnel token."""
        result = await self.session.execute(
            select(TunnelToken).where(
                TunnelToken.token == token,
                TunnelToken.is_active == True
            )
        )
        return result.scalars().first()

    async def get_user_tunnel_tokens(self, user_id: int) -> list[TunnelToken]:
        """Get all tunnel tokens for a specific user."""
        result = await self.session.execute(
            select(TunnelToken).where(
                TunnelToken.user_id == user_id,
                TunnelToken.is_active == True
            )
        )
        return list(result.scalars().all())

    async def get_public_tunnel_tokens(self) -> list[TunnelToken]:
        """Get all public tunnel tokens."""
        result = await self.session.execute(
            select(TunnelToken).where(
                TunnelToken.is_public == True,
                TunnelToken.is_active == True
            )
        )
        return list(result.scalars().all())

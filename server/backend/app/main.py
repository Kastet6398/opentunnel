"""Main application module."""

import asyncio
from typing import Optional

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from .api.v1 import auth, health, ingress, tunnels
from .core.config import settings
from .core.database import init_db, AsyncSessionLocal
from .middleware import setup_cors, setup_logging
from .services import TunnelRegistry, TunnelService
from .utils import ORJSONResponse
from .utils.exceptions import (
    pydantic_validation_exception_handler,
    validation_exception_handler
)

# Setup logging
setup_logging()

# Create registry - tunnel service will be created during startup
registry = TunnelRegistry()

# Inject registry dependency only for now
tunnels.get_tunnel_registry._registry = registry


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="RouteTunnel",
        description="A tunnel service for routing requests",
        version="1.0.0",
        default_response_class=ORJSONResponse
    )
    
    # Setup middleware
    setup_cors(app)
    
    # Add exception handlers
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
    
    # Include routers
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(tunnels.router)
    app.include_router(ingress.router)
    
    # Startup event
    @app.on_event("startup")
    async def startup() -> None:
        """Application startup event."""
        # Initialize database
        await init_db()

        # Create session and initialize tunnel service with it
        session = AsyncSessionLocal()
        tunnel_service = TunnelService(registry=registry, session=session)

        # Inject service dependencies
        tunnels.get_tunnel_service._service = tunnel_service
        ingress.get_tunnel_service._service = tunnel_service

        # Store session and service in app state to prevent garbage collection
        app.state._db_session = session
        app.state._tunnel_service = tunnel_service
        
        async def ping_task() -> None:
            """Background task to ping connected tunnels."""
            while True:
                try:
                    await registry.ping_connected()
                except Exception as exc:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning("Ping task error: %s", exc)
                await asyncio.sleep(settings.ping_interval)
        
        app.state._ping_task = asyncio.create_task(ping_task())
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown() -> None:
        """Application shutdown event."""
        # Cancel ping task
        task: Optional[asyncio.Task] = getattr(app.state, "_ping_task", None)
        if task:
            task.cancel()
            
        # Close database session
        session = getattr(app.state, "_db_session", None)
        if session:
            await session.close()
    
    return app


# Create the application instance
app = create_app()
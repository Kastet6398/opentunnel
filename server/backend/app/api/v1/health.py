"""Health check endpoints."""

from typing import Dict

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/")
async def root() -> Dict[str, str]:
    """Root health check endpoint."""
    return {"status": "ok"}


@router.get("/health")
async def health() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
"""Ingress-related data models."""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class IngressRequest(BaseModel):
    """Request model for ingress traffic."""
    
    correlation_id: str = Field(..., description="Unique identifier for request correlation")
    method: str = Field(..., description="HTTP method")
    path: str = Field(..., description="Request path")
    query: Dict[str, List[str]] = Field(..., description="Query parameters")
    headers: Dict[str, str] = Field(..., description="Request headers")
    body_b64: Optional[str] = Field(None, description="Base64 encoded request body")


class IngressResponse(BaseModel):
    """Response model for ingress traffic."""
    
    correlation_id: str = Field(..., description="Unique identifier for response correlation")
    status_code: int = Field(..., description="HTTP status code")
    headers: Dict[str, str] = Field(..., description="Response headers")
    body_b64: Optional[str] = Field(None, description="Base64 encoded response body")
    error: Optional[str] = Field(None, description="Error message if any")
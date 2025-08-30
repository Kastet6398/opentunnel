"""Exception handlers for the application."""

import json
from typing import Any, Dict, List, Union

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from .response import ORJSONResponse


def safe_serialize(obj: Any) -> Any:
    """Safely serialize an object for JSON output."""
    if obj is None:
        return None
    
    # Handle basic JSON-serializable types
    if isinstance(obj, (str, int, float, bool)):
        return obj
    
    # Handle lists and dicts
    if isinstance(obj, list):
        return [safe_serialize(item) for item in obj]
    
    if isinstance(obj, dict):
        return {str(k): safe_serialize(v) for k, v in obj.items()}
    
    # For non-serializable objects, convert to string representation
    try:
        # Try to serialize the object
        json.dumps(obj)
        return obj
    except (TypeError, ValueError):
        # If serialization fails, return string representation
        return str(obj)


class ValidationErrorDetail:
    """Represents a single validation error detail."""
    
    def __init__(
        self,
        type: str,
        loc: List[Union[str, int]],
        msg: str,
        input: Any = None,
        ctx: Dict[str, Any] = None
    ):
        self.type = type
        self.loc = loc
        self.msg = msg
        self.input = safe_serialize(input)
        self.ctx = safe_serialize(ctx) or {}


def format_validation_error(error: ValidationError) -> List[Dict[str, Any]]:
    """Format a Pydantic ValidationError into the standard format."""
    details = []
    
    for err in error.errors():
        # Extract location path
        loc = list(err.get("loc", []))
        
        # Map Pydantic error types to standard types
        error_type = err.get("type", "value_error")
        if error_type.startswith("type_error"):
            error_type = "type_error"
        elif error_type.startswith("value_error"):
            error_type = "value_error"
        elif error_type.startswith("missing"):
            error_type = "missing"
        
        # Get the error message
        msg = err.get("msg", "Validation error")
        
        # Get the input value that caused the error and safely serialize it
        input_value = safe_serialize(err.get("input"))
        
        # Get context (additional error information) and safely serialize it
        ctx = safe_serialize(err.get("ctx", {}))
        
        details.append({
            "type": error_type,
            "loc": loc,
            "msg": msg,
            "input": input_value,
            "ctx": ctx
        })
    
    return details


def create_auth_error_detail(
    error_type: str,
    location: List[str],
    message: str,
    input_value: Any = None,
    context: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Create a standardized auth error detail object."""
    return {
        "type": error_type,
        "loc": location,
        "msg": message,
        "input": safe_serialize(input_value),
        "ctx": safe_serialize(context) or {}
    }


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> ORJSONResponse:
    """Handle Pydantic validation errors."""
    details = format_validation_error(exc)
    
    return ORJSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": details}
    )


async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> ORJSONResponse:
    """Handle direct Pydantic validation errors."""
    details = format_validation_error(exc)
    
    return ORJSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": details}
    )
"""Custom response classes."""

import orjson
from fastapi.responses import JSONResponse


class ORJSONResponse(JSONResponse):
    """Custom JSON response using orjson for better performance."""
    
    media_type = "application/json"

    def render(self, content: object) -> bytes:
        """Render content using orjson."""
        return orjson.dumps(content)
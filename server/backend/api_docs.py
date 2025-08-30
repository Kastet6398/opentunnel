#!/usr/bin/env python3
"""Generate API documentation."""

import json
from app.main import app


def generate_openapi_docs():
    """Generate OpenAPI documentation."""
    openapi_schema = app.openapi()
    
    # Save to file
    with open("openapi.json", "w") as f:
        json.dump(openapi_schema, f, indent=2)
    
    print("OpenAPI documentation generated: openapi.json")
    print("\nYou can view the interactive docs at:")
    print("http://localhost:8000/docs")
    print("\nOr view the ReDoc at:")
    print("http://localhost:8000/redoc")


if __name__ == "__main__":
    generate_openapi_docs()
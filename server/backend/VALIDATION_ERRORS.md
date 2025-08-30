# Validation Error Handling

This document describes the validation error handling implementation in the RouteTunnel backend.

## Overview

The application now includes comprehensive validation error handling that returns standardized error responses in the format specified by the user. All validation errors are handled consistently across the application.

## Error Response Format

When a validation error occurs, the API returns a response with the following structure:

```json
{
    "detail": [
        {
            "type": "value_error",
            "loc": ["body", "phone_number"],
            "msg": "Value error, Invalid phone number",
            "input": "+11234567890",
            "ctx": {
                "error": {}
            }
        }
    ]
}
```

### Field Descriptions

- **`type`**: The type of validation error (e.g., `value_error`, `type_error`, `missing`)
- **`loc`**: The location of the error in the request (e.g., `["body", "field_name"]`)
- **`msg`**: A human-readable error message
- **`input`**: The actual input value that caused the error
- **`ctx`**: Additional context information about the error

## Implementation Details

### Exception Handlers

The validation error handling is implemented in `/backend/app/utils/exceptions.py`:

- `validation_exception_handler`: Handles FastAPI's `RequestValidationError`
- `pydantic_validation_exception_handler`: Handles direct Pydantic `ValidationError`
- `safe_serialize`: Safely serializes objects for JSON output, handling non-serializable objects

### Registration

Exception handlers are registered in the main application (`/backend/app/main.py`):

```python
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
```

### Error Type Mapping

The implementation maps Pydantic error types to standardized types:

- `type_error.*` → `type_error`
- `value_error.*` → `value_error`
- `missing` → `missing`

### Safe Serialization

The implementation includes a `safe_serialize` function that handles non-JSON-serializable objects (like exceptions) by converting them to their string representation. This prevents JSON serialization errors when validation errors contain complex objects.

## Examples

### Phone Number Validation

When an invalid phone number is provided:

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "phone_number": "+11234567890",
    "password": "testpassword123"
  }'
```

Response (422 Unprocessable Entity):
```json
{
    "detail": [
        {
            "type": "value_error",
            "loc": ["body", "phone_number"],
            "msg": "Value error, Invalid phone number",
            "input": "+11234567890",
            "ctx": {}
        }
    ]
}
```

### Email Validation

When an invalid email is provided:

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "invalid-email",
    "phone_number": "+1234567890",
    "password": "testpassword123"
  }'
```

Response (422 Unprocessable Entity):
```json
{
    "detail": [
        {
            "type": "value_error",
            "loc": ["body", "email"],
            "msg": "value is not a valid email address",
            "input": "invalid-email",
            "ctx": {}
        }
    ]
}
```

### Missing Required Fields

When required fields are missing:

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com"
  }'
```

Response (422 Unprocessable Entity):
```json
{
    "detail": [
        {
            "type": "missing",
            "loc": ["body", "phone_number"],
            "msg": "Field required",
            "input": null,
            "ctx": {}
        },
        {
            "type": "missing",
            "loc": ["body", "password"],
            "msg": "Field required",
            "input": null,
            "ctx": {}
        }
    ]
}
```

## Testing

Two test scripts are provided to verify the validation error handling:

1. **`test_validation.py`**: Simple test for phone number validation
2. **`test_validation_comprehensive.py`**: Comprehensive tests for various validation scenarios

To run the tests:

```bash
# Start the server first
uvicorn app.main:app --reload

# In another terminal, run the tests
python3 test_validation.py
python3 test_validation_comprehensive.py
```

## Status Codes

All validation errors return HTTP status code `422 Unprocessable Entity`, which is the standard for validation errors in REST APIs.

## Compatibility

This implementation is compatible with:
- FastAPI 0.112.2+
- Pydantic 2.8.2+
- All existing validation logic in the application

The error handling is transparent to existing code and doesn't require any changes to existing endpoints or models.
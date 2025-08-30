# RouteTunnel Backend

A FastAPI-based tunnel service that allows creating tunnels and forwarding requests through WebSocket connections.

## Project Structure

```
app/
├── api/                    # API endpoints
│   ├── v1/                # API version 1
│   │   ├── health.py      # Health check endpoints
│   │   ├── ingress.py     # Public tunnel access endpoints
│   │   └── tunnels.py     # Tunnel management endpoints
│   └── dependencies/      # API dependencies
├── core/                  # Core application components
│   ├── config.py         # Configuration management
│   └── security.py       # Security utilities
├── middleware/            # Custom middleware
│   ├── cors.py           # CORS configuration
│   └── logging.py        # Logging setup
├── models/               # Data models and schemas
│   ├── tunnel.py         # Tunnel-related models
│   └── ingress.py        # Ingress-related models
├── services/             # Business logic services
│   ├── registry.py       # Tunnel registry service
│   └── tunnel_service.py # Tunnel business logic
├── utils/                # Utility functions
│   └── response.py       # Custom response classes
└── main.py              # Application entry point

tests/                   # Test suite
├── conftest.py         # Test configuration
└── test_health.py      # Health endpoint tests
```

## Features

- **User Authentication**: JWT-based authentication with email, phone, and password
- **Tunnel Management**: Create, list, and delete tunnels (requires authentication)
- **WebSocket Communication**: Real-time tunnel connections
- **Request Forwarding**: Forward HTTP requests through tunnels
- **Database Support**: SQLAlchemy with async support
- **Configuration Management**: Environment-based configuration
- **Health Checks**: Built-in health monitoring
- **CORS Support**: Configurable CORS middleware
- **Testing**: Comprehensive test suite

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy environment configuration:
```bash
cp .env.example .env
```

3. Update `.env` with your configuration

## Running the Application

### Development
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Docker
```bash
docker build -t routetunnel .
docker run -p 8000:8000 routetunnel
```

## Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app
```

## API Endpoints

### Health
- `GET /` - Root health check
- `GET /health` - Health status

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login with email and password
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - Logout (revoke refresh token)
- `GET /api/auth/me` - Get current user information
- `PUT /api/auth/me` - Update current user information
- `POST /api/auth/change-password` - Change user password

### Tunnels (Requires Authentication)
- `POST /api/tunnels` - Create a tunnel
- `GET /api/tunnels` - List all tunnels
- `DELETE /api/tunnels/{route}` - Delete a tunnel
- `WS /ws/tunnel?token={token}` - WebSocket connection

### Ingress
- `* /r/{route}` - Access tunnel (any HTTP method)
- `* /r/{route}/{path:path}` - Access tunnel with sub-path

## Configuration

The application uses environment variables for configuration. See `.env.example` for all available options.

Key configuration options:
- `API_BASE_URL`: Base URL for API endpoints
- `WS_BASE_URL`: Base URL for WebSocket connections
- `PUBLIC_BASE_URL`: Public URL for tunnel access
- `TUNNEL_TIMEOUT`: Request timeout for tunnel forwarding
- `PING_INTERVAL`: Interval for pinging connected tunnels
- `SECRET_KEY`: JWT secret key (change in production)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Access token expiration time
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiration time
- `DATABASE_URL`: Database connection URL

## Authentication Usage

### Register a User
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "phone_number": "+1234567890",
    "password": "securepassword123"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Use Authenticated Endpoints
```bash
# Get access token from login response, then:
curl -X GET "http://localhost:8000/api/tunnels" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Create a Tunnel (Authenticated)
```bash
curl -X POST "http://localhost:8000/api/tunnels" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "route": "my-tunnel",
    "description": "My personal tunnel"
  }'
```

## Architecture

The application follows a layered architecture:

1. **API Layer**: FastAPI routes and endpoints
2. **Service Layer**: Business logic and operations
3. **Model Layer**: Data models and validation
4. **Core Layer**: Configuration and utilities
5. **Database Layer**: SQLAlchemy models and database operations

This structure provides:
- Clear separation of concerns
- Easy testing and mocking
- Scalable code organization
- Maintainable codebase
- Secure authentication and authorization
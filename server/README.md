# RouteTunnel

A modern tunnel service with a web-based management interface. RouteTunnel allows you to create secure tunnels and manage them through an intuitive web dashboard.

## Features

- **Secure Authentication**: User registration and login with JWT tokens
- **Tunnel Management**: Create, monitor, and delete tunnels through a web interface
- **Real-time Status**: Monitor tunnel connection status in real-time
- **Modern UI**: Clean, responsive web interface built with React and Tailwind CSS
- **RESTful API**: FastAPI backend with comprehensive API documentation
- **WebSocket Support**: Real-time tunnel communication

## Architecture

- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Authentication**: JWT tokens with refresh token support
- **Database**: PostgreSQL with Alembic migrations

## Quick Start

### Using Docker Compose (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd opentunnel/backend/a/server
```

2. Start all services:
```bash
docker-compose up -d
```

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Manual Setup

#### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. Start the backend server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API URL
```

4. Start the development server:
```bash
npm run dev
```

## Usage

1. **Register an Account**: Visit the frontend and create a new account
2. **Create a Tunnel**: Use the dashboard to create a new tunnel
3. **Connect Your Client**: Use the provided WebSocket URL and token to connect your tunnel client
4. **Monitor Status**: View real-time tunnel status in the dashboard

## API Documentation

The backend provides comprehensive API documentation at `/docs` when running. Key endpoints include:

- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/tunnels` - Create a tunnel
- `GET /api/tunnels` - List tunnels
- `DELETE /api/tunnels/{route}` - Delete a tunnel
- `WS /api/tunnels/ws/tunnel` - WebSocket tunnel connection

## Development

### Backend Development

- FastAPI with automatic API documentation
- SQLAlchemy ORM with async support
- Alembic for database migrations
- Pytest for testing

### Frontend Development

- React 18 with TypeScript
- Vite for fast development
- Tailwind CSS for styling
- React Router for navigation
- Axios for API communication

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
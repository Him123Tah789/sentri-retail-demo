# Sentri Retail Demo - Backend API

FastAPI-based backend service for the Sentri Retail Demo application.

## Features

- **RESTful API**: Clean, documented endpoints
- **Authentication**: JWT-based security
- **Guardian Engine**: Security monitoring service
- **AI Assistant**: Intelligent chat interface
- **Risk Assessment**: Security scanning and analysis
- **Real-time Data**: Live updates and monitoring

## Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: SQLAlchemy with SQLite
- **Authentication**: JWT tokens
- **Validation**: Pydantic schemas
- **Testing**: Pytest
- **Documentation**: Auto-generated OpenAPI/Swagger

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Database Setup

```bash
# Initialize database with demo data
python -m app.db.seed_demo
```

## API Endpoints

### Health Check
- `GET /health` - System health status

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/logout` - User logout
- `GET /api/v1/auth/me` - Current user info

### Security Scans
- `POST /api/v1/scans/url` - Scan URL for security risks
- `POST /api/v1/scans/email` - Analyze email content
- `GET /api/v1/scans/history` - Scan history

### Guardian Engine
- `GET /api/v1/guardian/status` - Guardian system status
- `GET /api/v1/guardian/alerts` - Active security alerts
- `POST /api/v1/guardian/configure` - Update configuration

### AI Assistant
- `POST /api/v1/assistant/chat` - Send chat message
- `GET /api/v1/assistant/history` - Chat history
- `POST /api/v1/assistant/analyze` - Analyze content

## Configuration

Environment variables (see `.env.example`):
- `DATABASE_URL` - Database connection string
- `SECRET_KEY` - JWT signing key
- `DEBUG` - Debug mode flag
- `ALLOWED_ORIGINS` - CORS allowed origins

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn app.main:app --reload

# View API documentation
# http://localhost:8000/docs
```
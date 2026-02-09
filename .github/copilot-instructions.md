# Sentri Retail Demo - Copilot Instructions

This project is a retail security and risk management demo system with the following components:

## Project Structure
- **Backend**: FastAPI with Python 3.9+
- **Frontend**: Next.js with TypeScript and React
- **Database**: SQLite for demo (configurable)
- **Infrastructure**: Docker containers for easy deployment

## Key Features
- Guardian Engine for security monitoring
- AI Assistant for retail insights
- Risk scanning and analysis
- Real-time dashboard with insights
- Authentication and user management

## Development Guidelines
- Use TypeScript for all frontend code
- Follow FastAPI patterns for backend endpoints
- Implement proper error handling and logging
- Use Pydantic models for API schemas
- Follow React functional component patterns
- Use Material-UI or similar for consistent styling

## API Patterns
- RESTful endpoints under `/api/v1/`
- Proper HTTP status codes
- Structured JSON responses
- Authentication using JWT tokens
- Input validation using Pydantic schemas

## Security Considerations
- Environment variables for sensitive data
- Proper CORS configuration
- Input sanitization
- Rate limiting for API endpoints
- Secure token handling
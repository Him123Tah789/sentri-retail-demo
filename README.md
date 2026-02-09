# Sentri Retail Demo

A comprehensive retail security and risk management system with AI-powered insights and real-time monitoring.

## Overview

Sentri Retail Demo is a full-stack application that demonstrates advanced security scanning, risk assessment, and AI-powered assistance for retail operations. The system features real-time monitoring, intelligent threat detection, and actionable insights through an intuitive dashboard.

## Features

- **Guardian Engine**: Real-time security monitoring and threat detection
- **AI Assistant**: Intelligent chat interface for retail insights and analysis
- **Risk Scanning**: Comprehensive security assessment tools
- **Real-time Dashboard**: Live insights and analytics
- **Authentication**: Secure user management and authorization

## Architecture

- **Backend**: FastAPI with Python 3.9+
- **Frontend**: Next.js with TypeScript and React
- **Database**: SQLite (configurable for other databases)
- **Infrastructure**: Docker containers for easy deployment

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- Docker and Docker Compose

### Running with Docker

```bash
cd infra/docker
docker-compose -f docker-compose.demo.yml up --build
```

### Manual Setup

#### Backend

```bash
cd app/backend
pip install -r requirements.txt
python -m app.main
```

#### Frontend

```bash
cd app/frontend
npm install
npm run dev
```

## Project Structure

```
sentri-retail-demo/
├── app/
│   ├── backend/          # FastAPI backend
│   └── frontend/         # Next.js frontend
├── demo/                 # Demo materials and assets
├── infra/               # Infrastructure and deployment
└── docs/                # Documentation
```

## API Documentation

Once running, visit:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Security

Please review [SECURITY.md](SECURITY.md) for security considerations and [PRIVACY.md](PRIVACY.md) for privacy policies.

## License

This project is licensed under the MIT License - see [LICENSE.md](LICENSE.md) for details.
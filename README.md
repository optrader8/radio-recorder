# Radio Recorder

A headless radio recording system with web dashboard for Ubuntu servers. Records internet radio streams automatically without physical audio devices, manages files through a web interface, and provides AI-powered content analysis.

## Features

- **Automated Recording**: Schedule or immediately start recordings from internet radio streams
- **Multiple Protocols**: Support for HLS, HTTP/HTTPS, RTMP, and MMS streams
- **Web Dashboard**: Real-time monitoring and control through a modern web interface
- **File Management**: Organize, search, convert, and download recordings
- **AI Analysis**: Transcription, summarization, and speaker identification
- **Containerized**: Full Docker setup for easy deployment and scaling

## Architecture

- **Backend**: FastAPI with async support, SQLAlchemy, Celery for background tasks
- **Frontend**: React 18 with TypeScript, TanStack Router/Query, Tailwind CSS
- **Database**: PostgreSQL with Alembic migrations
- **Message Queue**: Redis with Celery workers
- **Audio Processing**: FFmpeg for recording and format conversion
- **Storage**: Configurable local or S3-compatible storage

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd radio-recorder
```

2. Copy environment configuration:
```bash
cp .env.example .env
```

3. Edit `.env` file with your configuration:
```bash
# Required: Generate a secure secret key
SECRET_KEY=your-very-secure-secret-key-here

# Optional: Add AI service keys for transcription features
WHISPER_API_KEY=your-whisper-api-key
OPENAI_API_KEY=your-openai-api-key
```

4. Start the services:
```bash
docker-compose up -d
```

5. Run database migrations:
```bash
docker-compose exec backend alembic upgrade head
```

6. Access the application:
- Web Dashboard: http://localhost
- API Documentation: http://localhost/api/v1/docs
- Backend API: http://localhost:8000

## Development

### Backend Development

```bash
cd apps/backend

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload

# Run tests
pytest
```

### Frontend Development

```bash
cd apps/frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

## API Usage

```bash
# Get system health
curl "http://localhost:8000/api/v1/health"

# API documentation available at:
# http://localhost:8000/api/v1/docs
```

## Project Status

This is the initial project setup. The foundation is complete with:

✅ **Infrastructure Setup**
- Docker Compose configuration
- PostgreSQL database with migrations
- Redis for message queuing
- Nginx reverse proxy setup

✅ **Backend Foundation**
- FastAPI application structure
- SQLAlchemy models and database layer
- Alembic migrations
- Basic API endpoints structure
- Logging and configuration management

✅ **Frontend Foundation**
- React 18 with TypeScript
- TanStack Router for routing
- TanStack Query for server state
- Tailwind CSS for styling
- Basic pages and components

🚧 **Next Steps** (To be implemented):
- Authentication and authorization system
- Celery task queue implementation
- Recording service with FFmpeg integration
- Audio processing capabilities
- File management system
- AI analysis integration
- Complete API endpoints
- Frontend components and features

## License

[Add your license information here]
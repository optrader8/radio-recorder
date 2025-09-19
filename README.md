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
- Docker Compose configuration with all services (PostgreSQL, Redis, Nginx, Celery)
- PostgreSQL database with migrations and complete data models
- Redis for message queuing and caching
- Nginx reverse proxy with proper routing
- Multi-container orchestration ready for production

✅ **Backend Foundation**
- FastAPI application with full async support
- Complete SQLAlchemy models (Recording, RadioStation, Schedule, User, AIAnalysis)
- Alembic migrations with initial schema
- API endpoints structure for all major features
- Celery integration for background tasks (workers and beat scheduler)
- Comprehensive logging and configuration management

✅ **Frontend Foundation**
- React 18 with TypeScript and strict type checking
- TanStack Router for type-safe routing
- TanStack Query for server state management
- Tailwind CSS with responsive design system
- Component architecture ready for expansion

🚧 **Implementation Priority** (Based on system analysis):

**Phase 1 - Core Recording Engine** ✅ **COMPLETED**
- ✅ Replaced FFmpeg simulation with real Streamlink+FFmpeg implementation
- ✅ Implemented headless HLS stream capture for Ubuntu servers
- ✅ Added CBS radio station support with m3u8 playlists
- ✅ Error handling and retry mechanisms implemented

**Phase 2 - Real-time Features**
- WebSocket integration for live recording status
- Real-time dashboard monitoring
- Live audio streaming preview
- Progress tracking and cancellation

**Phase 3 - Advanced Processing**
- Audio format conversion pipeline
- Automatic file compression and optimization
- Metadata extraction from streams
- Post-processing workflow integration

**Phase 4 - AI Integration**
- Whisper API transcription service
- Content summarization with LLM
- Speaker diarization implementation
- Automated tagging and categorization

## 🎯 Claude Opus 대화 통합 결과 ✅ **구현 완료**

**5가지 헤드리스 녹음 방법 중 우선 순위 1번 구현 완료:**

1. ✅ **Streamlink + FFmpeg** - CBS 라디오 HLS 스트림 완벽 지원
2. 🚧 **직접 HLS/DASH 처리** - 필요시 구현 예정
3. 🚧 **yt-dlp 플랫폼 특화** - YouTube, Twitch 지원 예정
4. 🚧 **비동기 스트림 처리** - 다중 스트림용 확장 예정
5. ✅ **Docker 격리 환경** - 현재 구조에 완전 통합

## 🎵 CBS 라디오 녹음 기능

**지원 방송국** (자동 추가됨):
- CBS 표준FM (98.1MHz)
- CBS 음악FM (93.9MHz)
- CBS Joy4You
- 각 방송국별 백업 스트림 URL

**실제 녹음 예시**:
```bash
# 30초 테스트 녹음
python test_cbs_recording.py

# Docker에서 실제 서비스 실행
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

**구현된 기능**:
- ✅ HLS m3u8 플레이리스트 자동 파싱
- ✅ 네트워크 끊김 시 자동 재시도 (5회)
- ✅ 지정 시간 녹음 후 자동 종료
- ✅ MP3 포맷 직접 저장
- ✅ 비동기 처리로 다중 녹음 지원
- ✅ 파일 크기 자동 계산

자세한 구현 내용은 `INTEGRATION_ANALYSIS.md`와 `IMPLEMENTATION_ROADMAP.md`를 참조하세요.

## License

[Add your license information here]
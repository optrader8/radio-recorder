# Design Document

## Overview

Radio Recorder는 마이크로서비스 아키텍처를 기반으로 한 헤드리스 라디오 녹음 시스템입니다. 시스템은 FastAPI 백엔드, React 프론트엔드, 그리고 여러 지원 서비스들로 구성되어 Docker 컨테이너 환경에서 실행됩니다. 핵심 설계 원칙은 확장성, 신뢰성, 그리고 사용자 친화적인 인터페이스입니다.

## Architecture

### High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        WEB[Web Dashboard]
        API_CLIENT[API Clients]
    end
    
    subgraph "Load Balancer"
        NGINX[Nginx Reverse Proxy]
    end
    
    subgraph "Application Layer"
        BACKEND[FastAPI Backend]
        FRONTEND[React Frontend]
    end
    
    subgraph "Service Layer"
        RECORDER[Recording Service]
        SCHEDULER[Scheduler Service]
        PROCESSOR[Audio Processor]
        AI_SERVICE[AI Analysis Service]
    end
    
    subgraph "Message Queue"
        REDIS[Redis]
        CELERY[Celery Workers]
    end
    
    subgraph "Data Layer"
        POSTGRES[PostgreSQL]
        STORAGE[File Storage]
    end
    
    subgraph "External Services"
        WHISPER[Whisper API]
        LLM[LLM Services]
    end
    
    WEB --> NGINX
    API_CLIENT --> NGINX
    NGINX --> BACKEND
    NGINX --> FRONTEND
    
    BACKEND --> RECORDER
    BACKEND --> SCHEDULER
    BACKEND --> PROCESSOR
    BACKEND --> AI_SERVICE
    
    RECORDER --> REDIS
    SCHEDULER --> REDIS
    PROCESSOR --> REDIS
    AI_SERVICE --> REDIS
    
    REDIS --> CELERY
    
    BACKEND --> POSTGRES
    CELERY --> POSTGRES
    CELERY --> STORAGE
    
    AI_SERVICE --> WHISPER
    AI_SERVICE --> LLM
```

### Container Architecture

```mermaid
graph TB
    subgraph "Docker Compose Environment"
        subgraph "Web Tier"
            NGINX_C[nginx:alpine]
            FRONTEND_C[radio-recorder-frontend]
        end
        
        subgraph "Application Tier"
            BACKEND_C[radio-recorder-backend]
            WORKER_C[celery-worker]
            BEAT_C[celery-beat]
        end
        
        subgraph "Data Tier"
            POSTGRES_C[postgres:15]
            REDIS_C[redis:alpine]
        end
        
        subgraph "Storage"
            RECORDINGS[Volume: recordings]
            DB_DATA[Volume: postgres_data]
        end
    end
    
    NGINX_C --> FRONTEND_C
    NGINX_C --> BACKEND_C
    BACKEND_C --> POSTGRES_C
    BACKEND_C --> REDIS_C
    WORKER_C --> REDIS_C
    WORKER_C --> POSTGRES_C
    BEAT_C --> REDIS_C
    WORKER_C --> RECORDINGS
    POSTGRES_C --> DB_DATA
```

## Components and Interfaces

### Backend API Service

**Technology Stack:**
- FastAPI with async/await support
- SQLAlchemy ORM with async support
- Pydantic for data validation
- JWT authentication
- CORS middleware

**Key Modules:**
- `app/api/`: REST API endpoints
- `app/core/`: Core business logic and configuration
- `app/models/`: Database models
- `app/services/`: Business service layer
- `app/workers/`: Celery background tasks

**API Endpoints:**
```python
# Recording Management
POST   /api/v1/recordings          # Start recording
GET    /api/v1/recordings          # List recordings
GET    /api/v1/recordings/{id}     # Get recording details
DELETE /api/v1/recordings/{id}     # Delete recording
PUT    /api/v1/recordings/{id}/stop # Stop active recording

# Schedule Management
POST   /api/v1/schedules           # Create schedule
GET    /api/v1/schedules           # List schedules
PUT    /api/v1/schedules/{id}      # Update schedule
DELETE /api/v1/schedules/{id}      # Delete schedule

# File Management
GET    /api/v1/files               # List files
GET    /api/v1/files/{id}/download # Download file
POST   /api/v1/files/{id}/convert  # Convert file format
DELETE /api/v1/files/{id}          # Delete file

# AI Services
POST   /api/v1/ai/transcribe       # Transcribe audio
POST   /api/v1/ai/summarize        # Summarize content
POST   /api/v1/ai/analyze          # Analyze content

# System
GET    /api/v1/health              # Health check
GET    /api/v1/stats               # System statistics
```

### Frontend Web Application

**Technology Stack:**
- React 18 with TypeScript
- Vite for build tooling
- TanStack Router for routing
- TanStack Query for server state
- Zustand for client state
- Radix UI for components
- Tailwind CSS for styling
- WaveSurfer.js for audio visualization

**Key Components:**
- Dashboard: Real-time system overview
- Recording Manager: Start/stop recordings
- Schedule Manager: CRUD operations for schedules
- File Browser: Browse and manage recordings
- Audio Player: Playback with waveform visualization
- Settings: System configuration

### Recording Service

**Core Functionality:**
- Stream capture using FFmpeg
- Multiple format support (MP3, AAC, FLAC, OGG)
- Concurrent recording management
- Automatic retry and error recovery
- Metadata extraction and tagging

**Implementation:**
```python
class RecordingService:
    async def start_recording(self, stream_url: str, config: RecordingConfig) -> Recording
    async def stop_recording(self, recording_id: str) -> bool
    async def get_recording_status(self, recording_id: str) -> RecordingStatus
    async def list_active_recordings(self) -> List[Recording]
```

### Scheduler Service

**Core Functionality:**
- Cron-like scheduling with APScheduler
- One-time and recurring schedules
- Schedule conflict detection
- Automatic cleanup of expired schedules

**Implementation:**
```python
class SchedulerService:
    async def create_schedule(self, schedule: ScheduleCreate) -> Schedule
    async def update_schedule(self, schedule_id: str, updates: ScheduleUpdate) -> Schedule
    async def delete_schedule(self, schedule_id: str) -> bool
    async def get_upcoming_schedules(self, hours: int = 24) -> List[Schedule]
```

### Audio Processing Service

**Core Functionality:**
- Format conversion using FFmpeg
- Quality adjustment (bitrate, sample rate)
- Post-processing (silence removal, normalization)
- File splitting and merging

**Implementation:**
```python
class AudioProcessorService:
    async def convert_format(self, file_path: str, target_format: str, options: ConversionOptions) -> str
    async def split_file(self, file_path: str, split_config: SplitConfig) -> List[str]
    async def remove_silence(self, file_path: str, threshold: float) -> str
    async def normalize_audio(self, file_path: str, target_level: float) -> str
```

### AI Analysis Service

**Core Functionality:**
- Speech-to-text transcription
- Content summarization
- Keyword extraction
- Speaker diarization

**Implementation:**
```python
class AIAnalysisService:
    async def transcribe_audio(self, file_path: str) -> TranscriptionResult
    async def summarize_content(self, transcript: str) -> SummaryResult
    async def extract_keywords(self, transcript: str) -> List[Keyword]
    async def identify_speakers(self, file_path: str) -> SpeakerDiarizationResult
```

## Data Models

### Database Schema

```sql
-- Users table for authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Radio stations/sources
CREATE TABLE radio_stations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    stream_url VARCHAR(500) NOT NULL,
    description TEXT,
    genre VARCHAR(100),
    country VARCHAR(100),
    language VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Recording schedules
CREATE TABLE schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    station_id UUID REFERENCES radio_stations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    cron_expression VARCHAR(100) NOT NULL,
    duration_minutes INTEGER NOT NULL,
    format VARCHAR(10) DEFAULT 'mp3',
    bitrate INTEGER DEFAULT 128,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Recording sessions
CREATE TABLE recordings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    station_id UUID REFERENCES radio_stations(id) ON DELETE CASCADE,
    schedule_id UUID REFERENCES schedules(id) ON DELETE SET NULL,
    title VARCHAR(255),
    file_path VARCHAR(500),
    file_size BIGINT,
    duration_seconds INTEGER,
    format VARCHAR(10),
    bitrate INTEGER,
    sample_rate INTEGER,
    status VARCHAR(20) DEFAULT 'pending', -- pending, recording, completed, failed
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- AI analysis results
CREATE TABLE ai_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recording_id UUID REFERENCES recordings(id) ON DELETE CASCADE,
    analysis_type VARCHAR(50) NOT NULL, -- transcription, summary, keywords, speakers
    result JSONB NOT NULL,
    confidence_score FLOAT,
    processing_time_seconds INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- System configuration
CREATE TABLE system_config (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Audit log
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Pydantic Models

```python
# Base models
class BaseModel(PydanticBaseModel):
    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.isoformat()}

# User models
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

# Recording models
class RecordingConfig(BaseModel):
    format: AudioFormat = AudioFormat.MP3
    bitrate: int = 128
    sample_rate: int = 44100
    duration_minutes: Optional[int] = None

class RecordingCreate(BaseModel):
    station_id: UUID
    title: Optional[str] = None
    config: RecordingConfig = RecordingConfig()

class Recording(BaseModel):
    id: UUID
    user_id: UUID
    station_id: UUID
    title: Optional[str]
    file_path: Optional[str]
    file_size: Optional[int]
    duration_seconds: Optional[int]
    status: RecordingStatus
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime

# Schedule models
class ScheduleCreate(BaseModel):
    station_id: UUID
    name: str
    cron_expression: str
    duration_minutes: int
    config: RecordingConfig = RecordingConfig()

class Schedule(BaseModel):
    id: UUID
    user_id: UUID
    station_id: UUID
    name: str
    cron_expression: str
    duration_minutes: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
```

## Error Handling

### Error Categories

1. **Client Errors (4xx)**
   - 400 Bad Request: Invalid input data
   - 401 Unauthorized: Authentication required
   - 403 Forbidden: Insufficient permissions
   - 404 Not Found: Resource not found
   - 409 Conflict: Resource conflict (e.g., duplicate schedule)
   - 422 Unprocessable Entity: Validation errors

2. **Server Errors (5xx)**
   - 500 Internal Server Error: Unexpected server errors
   - 502 Bad Gateway: External service unavailable
   - 503 Service Unavailable: System overloaded
   - 507 Insufficient Storage: Storage quota exceeded

### Error Response Format

```python
class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str
```

### Recording Error Handling

```python
class RecordingErrorHandler:
    async def handle_stream_error(self, recording_id: str, error: Exception):
        """Handle stream connection errors with retry logic"""
        
    async def handle_storage_error(self, recording_id: str, error: Exception):
        """Handle storage-related errors"""
        
    async def handle_format_error(self, recording_id: str, error: Exception):
        """Handle audio format/encoding errors"""
```

### Retry Strategies

- **Stream Connection**: Exponential backoff with jitter (max 5 retries)
- **File Operations**: Linear backoff (max 3 retries)
- **External API Calls**: Exponential backoff (max 3 retries)
- **Database Operations**: Immediate retry once, then fail

## Testing Strategy

### Unit Testing

**Backend Testing:**
- pytest with async support
- Factory Boy for test data generation
- Mock external dependencies (FFmpeg, APIs)
- Database testing with pytest-postgresql

**Frontend Testing:**
- Vitest for unit tests
- React Testing Library for component tests
- MSW (Mock Service Worker) for API mocking

### Integration Testing

- Docker Compose test environment
- End-to-end API testing with real database
- File system integration tests
- External service integration tests (with mocks)

### Performance Testing

- Load testing with Locust
- Concurrent recording stress tests
- Storage performance benchmarks
- Memory usage profiling

### Test Coverage Goals

- Backend: >90% code coverage
- Frontend: >85% code coverage
- Critical paths: 100% coverage (recording, scheduling)

### Testing Infrastructure

```yaml
# docker-compose.test.yml
version: '3.8'
services:
  test-db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: radio_recorder_test
      POSTGRES_USER: test_user
      POSTGRES_PASSWORD: test_pass
    
  test-redis:
    image: redis:alpine
    
  test-backend:
    build:
      context: ./apps/backend
      dockerfile: Dockerfile.test
    depends_on:
      - test-db
      - test-redis
    environment:
      DATABASE_URL: postgresql://test_user:test_pass@test-db/radio_recorder_test
      REDIS_URL: redis://test-redis:6379
    command: pytest --cov=app --cov-report=xml
```

### Continuous Integration

```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run backend tests
        run: docker-compose -f docker-compose.test.yml run test-backend
      
  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: cd apps/frontend && npm ci
      - name: Run tests
        run: cd apps/frontend && npm test
```

이 설계 문서는 Radio Recorder 시스템의 전체적인 아키텍처, 주요 컴포넌트, 데이터 모델, 에러 처리, 그리고 테스트 전략을 포괄적으로 다루고 있습니다. 마이크로서비스 아키텍처를 기반으로 하여 확장성과 유지보수성을 고려했으며, 각 컴포넌트 간의 인터페이스와 데이터 흐름을 명확히 정의했습니다.
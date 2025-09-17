# Radio Recorder


헤드리스 환경에서 작동하는 라디오 방송 자동 녹음 및 관리 시스템

## 📋 목차

- [소개](#소개)
- [주요 기능](#주요-기능)
- [시스템 요구사항](#시스템-요구사항)
- [설치](#설치)
- [사용법](#사용법)
- [프로젝트 구조](#프로젝트-구조)
- [API 문서](#api-문서)
- [개발](#개발)
- [테스트](#테스트)
- [배포](#배포)
- [기여](#기여)
- [라이선스](#라이선스)

## 소개

Radio Recorder는 Ubuntu 서버에서 Docker 컨테이너로 실행되는 라디오 방송 녹음 시스템입니다. 물리적 사운드 디바이스 없이 인터넷 라디오 스트림을 녹음하고, 웹 대시보드를 통해 관리할 수 있습니다.

### 특징

- 🎙️ **다양한 스트림 지원**: HLS, HTTP/HTTPS, RTMP, MMS 등
- ⏰ **스케줄 녹음**: 원하는 시간에 자동으로 녹음 시작/종료
- 🎵 **다중 포맷**: MP3, AAC, FLAC, OGG 등 다양한 오디오 포맷
- 🤖 **AI 기능**: 음성 인식, 내용 요약, 키워드 추출
- 📊 **웹 대시보드**: 실시간 모니터링 및 관리
- 🐳 **컨테이너화**: Docker를 통한 간편한 배포

## 주요 기능

### 녹음 기능
- 실시간 라디오 스트림 캡처
- 예약 녹음 (일회성/반복)
- 동시 다중 채널 녹음
- 자동 재시도 및 오류 복구

### 오디오 처리
- 자동 포맷 변환
- 비트레이트 조정
- 무음 구간 제거
- 파일 분할 (시간/크기 기준)

### 관리 기능
- 웹 기반 대시보드
- 녹음 스케줄 관리
- 파일 브라우징 및 검색
- 통계 및 분석

### AI 확장 (선택적)
- 음성-텍스트 변환
- 내용 자동 요약
- 키워드 태깅
- 화자 분리

## 시스템 요구사항

### 최소 요구사항
- Ubuntu 20.04 LTS 이상
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM
- 2 CPU 코어
- 50GB 디스크 공간

### 권장 사양
- Ubuntu 22.04 LTS
- 8GB RAM
- 4 CPU 코어
- 500GB+ SSD
- 1Gbps 네트워크

## 설치

### 1. 저장소 클론

```bash
git clone https://github.com/yourusername/radio-recorder.git
cd radio-recorder
```

### 2. 환경 설정

```bash
# 환경 변수 파일 복사
cp .env.example .env

# 필수 환경 변수 설정
nano .env
```

`.env` 파일 예시:
```env
# Database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=radio_recorder
POSTGRES_USER=radio_user
POSTGRES_PASSWORD=secure_password

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# Storage
STORAGE_PATH=/data/recordings
MAX_STORAGE_GB=100

# API
API_HOST=0.0.0.0
API_PORT=8000
API_KEY=your_api_key

# Frontend
FRONTEND_PORT=3000
```

### 3. Docker 빌드 및 실행

```bash
# 모든 서비스 빌드
docker-compose build

# 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 4. 초기 설정

```bash
# 데이터베이스 마이그레이션
docker-compose exec backend python -m alembic upgrade head

# 관리자 계정 생성
docker-compose exec backend python scripts/create_admin.py
```

## 사용법

### 웹 대시보드 접속

브라우저에서 `http://your-server-ip:3000` 접속

### CLI 명령어

```bash
# 즉시 녹음 시작
docker-compose exec backend python -m app.cli record --url "https://stream.url" --duration 60

# 스케줄 추가
docker-compose exec backend python -m app.cli schedule add --url "https://stream.url" --time "10:00" --duration 120

# 녹음 목록 조회
docker-compose exec backend python -m app.cli list recordings

# 파일 변환
docker-compose exec backend python -m app.cli convert --input recording.wav --output recording.mp3
```

### API 사용 예시

```python
import requests

# 녹음 시작
response = requests.post(
    "http://localhost:8000/api/v1/recordings",
    json={
        "url": "https://stream.example.com",
        "duration": 3600,
        "format": "mp3",
        "bitrate": 128
    },
    headers={"X-API-Key": "your_api_key"}
)

# 스케줄 조회
response = requests.get(
    "http://localhost:8000/api/v1/schedules",
    headers={"X-API-Key": "your_api_key"}
)
```

## 프로젝트 구조

```
radio-recorder/
├── apps/
│   ├── backend/              # FastAPI 백엔드
│   │   ├── app/
│   │   │   ├── api/         # API 엔드포인트
│   │   │   ├── core/        # 핵심 로직
│   │   │   ├── models/      # 데이터 모델
│   │   │   ├── services/    # 비즈니스 로직
│   │   │   └── workers/     # 백그라운드 작업
│   │   ├── tests/           # 백엔드 테스트
│   │   └── requirements.txt
│   │
│   └── frontend/            # React 프론트엔드
│       ├── src/
│       │   ├── components/  # UI 컴포넌트
│       │   ├── pages/       # 페이지 컴포넌트
│       │   ├── hooks/       # 커스텀 훅
│       │   └── stores/      # 상태 관리
│       └── package.json
│
├── docker/                  # Docker 설정
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── nginx.conf
│
├── scripts/                 # 유틸리티 스크립트
├── docs/                    # 문서
├── docker-compose.yml
└── README.md
```

## API 문서

### 주요 엔드포인트

| 메소드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/v1/health` | 헬스 체크 |
| POST | `/api/v1/recordings` | 녹음 시작 |
| GET | `/api/v1/recordings` | 녹음 목록 조회 |
| DELETE | `/api/v1/recordings/{id}` | 녹음 삭제 |
| GET | `/api/v1/schedules` | 스케줄 목록 |
| POST | `/api/v1/schedules` | 스케줄 추가 |
| GET | `/api/v1/files` | 파일 목록 |
| GET | `/api/v1/files/{id}/download` | 파일 다운로드 |

전체 API 문서는 `http://localhost:8000/docs` (Swagger UI) 또는 `http://localhost:8000/redoc` (ReDoc)에서 확인할 수 있습니다.

## 개발

### 개발 환경 설정

```bash
# 백엔드 개발 서버
cd apps/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload

# 프론트엔드 개발 서버
cd apps/frontend
npm install
npm run dev
```

### 코드 스타일

```bash
# Python (Black, Flake8, isort)
black apps/backend
flake8 apps/backend
isort apps/backend

# TypeScript/React (ESLint, Prettier)
npm run lint
npm run format
```

## 테스트

```bash
# 백엔드 테스트
docker-compose exec backend pytest

# 프론트엔드 테스트
docker-compose exec frontend npm test

# E2E 테스트
npm run test:e2e
```

## 배포

### Production 배포

```bash
# Production 설정
cp .env.production .env

# 빌드 및 배포
docker-compose -f docker-compose.prod.yml up -d

# SSL 설정 (Let's Encrypt)
./scripts/setup-ssl.sh
```

### 백업

```bash
# 데이터베이스 백업
docker-compose exec postgres pg_dump -U radio_user radio_recorder > backup.sql

# 녹음 파일 백업
rsync -avz /data/recordings/ /backup/recordings/
```

## 모니터링

- **Prometheus**: `http://localhost:9090`
- **Grafana**: `http://localhost:3001`
- **로그**: Docker 로그 또는 `/var/log/radio-recorder/`

## 문제 해결

### 일반적인 문제

1. **녹음이 시작되지 않음**
   - 스트림 URL 확인
   - 네트워크 연결 확인
   - FFmpeg 로그 확인

2. **디스크 공간 부족**
   - 오래된 녹음 파일 정리
   - 스토리지 설정 조정

3. **메모리 부족**
   - 동시 녹음 수 제한
   - 워커 프로세스 수 조정

자세한 내용은 [문제 해결 가이드](docs/troubleshooting.md)를 참조하세요.

## 기여

프로젝트 기여를 환영합니다! [기여 가이드라인](CONTRIBUTING.md)을 읽어주세요.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 감사의 말

- FFmpeg 프로젝트
- FastAPI 커뮤니티
- React 생태계
- 모든 오픈소스 기여자들

## 연락처

- 프로젝트 링크: [https://github.com/yourusername/radio-recorder](https://github.com/yourusername/radio-recorder)
- 이슈 트래커: [https://github.com/yourusername/radio-recorder/issues](https://github.com/yourusername/radio-recorder/issues)

---

Made with ❤️ for radio enthusiasts
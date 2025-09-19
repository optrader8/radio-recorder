# Radio Recorder 구현 로드맵 ✅ **Phase 1 완료**
## Claude Opus 대화 기반 구체적 실행 계획

이 문서는 Claude Opus와의 대화에서 제시된 5가지 헤드리스 라디오 녹음 방법을 현재 프로젝트에 즉시 적용하기 위한 구체적인 실행 계획을 제시합니다.

## 🚀 즉시 실행 가능한 구현 계획

### **Week 1: 핵심 엔진 교체 (최우선)** ✅ **완료**

#### 1.1 의존성 추가 ✅ **완료**
```bash
# ✅ apps/backend/requirements.txt에 추가 완료
streamlink>=5.0.0
# 다른 의존성들은 필요에 따라 추후 추가 예정
```

#### 1.2 Docker 설정 확인 ✅ **완료**
```dockerfile
# ✅ apps/backend/Dockerfile - FFmpeg 이미 설치됨
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \  # ← 이미 설치되어 있었음
    curl \
    && rm -rf /var/lib/apt/lists/*

# ✅ streamlink는 Python 패키지로 설치됨 (pip install)
```

#### 1.3 recording_engine.py 완전 교체 ✅ **완료**

**이전 (시뮬레이션)** ❌
```python
# apps/backend/app/services/recording_engine.py:15-17 - 제거됨
async def _simulate_ffmpeg(recording: Recording) -> None:
    """Simulate an FFmpeg execution and update recording status."""
    await asyncio.sleep(0.1)  # ← 더 이상 시뮬레이션 아님
```

**현재 (실제 구현)** ✅
```python
import subprocess
import asyncio
import aiohttp
import aiofiles
from pathlib import Path
from typing import Optional

class MultiMethodRecorder:
    """Claude Opus 제시 방법들을 통합한 녹음 엔진"""

    @staticmethod
    async def record_with_streamlink(recording: Recording) -> bool:
        """방법 1: Streamlink + FFmpeg (가장 안정적)"""
        try:
            # 1단계: Streamlink로 스트림 URL 추출
            proc = await asyncio.create_subprocess_exec(
                "streamlink", recording.station.stream_url, "best", "--stream-url",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                return False

            stream_url = stdout.decode().strip()

            # 2단계: FFmpeg로 녹음
            output_path = Path(recording.file_path)
            ffmpeg_proc = await asyncio.create_subprocess_exec(
                "ffmpeg", "-i", stream_url,
                "-t", str(recording.duration_seconds),
                "-acodec", "libmp3lame",
                "-ab", "128k",
                "-f", "mp3",
                str(output_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            await ffmpeg_proc.communicate()
            return ffmpeg_proc.returncode == 0

        except Exception as e:
            logger.error(f"Streamlink recording failed: {e}")
            return False

    @staticmethod
    async def record_direct_stream(recording: Recording) -> bool:
        """방법 4: 직접 비동기 스트림 처리"""
        try:
            timeout = aiohttp.ClientTimeout(total=recording.duration_seconds + 30)

            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(recording.station.stream_url) as response:
                    if response.status != 200:
                        return False

                    output_path = Path(recording.file_path)
                    async with aiofiles.open(output_path, 'wb') as f:
                        start_time = asyncio.get_event_loop().time()

                        async for chunk in response.content.iter_chunked(1024*1024):
                            await f.write(chunk)

                            # 시간 체크
                            if asyncio.get_event_loop().time() - start_time > recording.duration_seconds:
                                break

                        return True

        except Exception as e:
            logger.error(f"Direct stream recording failed: {e}")
            return False

# 기존 _simulate_ffmpeg 함수 교체
async def _record_stream(recording: Recording) -> None:
    """실제 스트림 녹음 구현"""
    recorder = MultiMethodRecorder()

    # Fallback 전략: Streamlink → 직접 스트림
    success = await recorder.record_with_streamlink(recording)

    if not success:
        logger.warning(f"Streamlink failed for {recording.id}, trying direct stream")
        success = await recorder.record_direct_stream(recording)

    if not success:
        raise Exception("All recording methods failed")
```

### **Week 2: 통합 테스트 및 최적화** 🚧 **진행 중**

#### 2.1 테스트 스크립트 생성 ✅ **완료**
```python
# ✅ test_cbs_recording.py - 독립 테스트 스크립트 생성
# CBS 스트림 실제 테스트 가능

# 🚧 추후 단위 테스트 추가 예정
# apps/backend/tests/test_recording_engine.py
import pytest
from app.services.recording_engine import _record_with_streamlink

@pytest.mark.asyncio
async def test_streamlink_recording():
    # 실제 CBS 스트림 URL로 테스트
    pass
```

#### 2.2 CBS 방송국 데이터 추가 ✅ **완료**
```python
# ✅ alembic/versions/002_add_cbs_stations.py 생성
# 6개 CBS 라디오 방송국 자동 추가:
# - CBS 표준FM, 음악FM, Joy4You (메인 + 백업 URL)
```

#### 2.2 RadioStation 모델 확장
```python
# apps/backend/app/models/radio_station.py에 추가
class RadioStation(Base):
    # 기존 필드들...

    stream_type = Column(String(20), default="auto")  # auto, hls, http, rtmp
    recording_method = Column(String(20), default="streamlink")  # streamlink, direct, yt-dlp
    fallback_enabled = Column(Boolean, default=True)
```

#### 2.3 API 엔드포인트 업데이트
```python
# apps/backend/app/api/v1/endpoints/recordings.py
@router.post("/test-stream")
async def test_stream_recording(station_id: UUID):
    """스트림 녹음 테스트 엔드포인트"""
    # 30초 테스트 녹음으로 방법별 성공률 확인
    pass
```

### **Week 3-4: 고급 기능 구현**

#### 3.1 HLS 직접 처리 구현
```python
# apps/backend/app/services/hls_recorder.py
from idea.2.md의 HLSRecorder 클래스를 비동기로 변환하여 통합
```

#### 3.2 YouTube/Twitch 특화 처리
```python
# apps/backend/app/services/platform_recorders.py
import yt_dlp

class PlatformRecorder:
    @staticmethod
    async def record_youtube_live(recording: Recording):
        # Claude Opus yt-dlp 방법 비동기 구현
        pass
```

#### 3.3 실시간 진행률 WebSocket
```python
# apps/backend/app/api/websocket.py
from fastapi import WebSocket

@app.websocket("/ws/recording/{recording_id}")
async def recording_progress(websocket: WebSocket, recording_id: str):
    # 실시간 녹음 상태 전송
    pass
```

### **Week 5-6: 프론트엔드 통합**

#### 5.1 실시간 녹음 모니터링 컴포넌트
```typescript
// apps/frontend/src/components/RecordingMonitor.tsx
export function RecordingMonitor({ recordingId }: { recordingId: string }) {
    // WebSocket으로 실시간 진행률 표시
    // 녹음 시작/중지 컨트롤
    // 에러 상태 표시
}
```

#### 5.2 스트림 테스트 도구
```typescript
// apps/frontend/src/components/StreamTester.tsx
export function StreamTester() {
    // 스트림 URL 입력
    // 방법별 테스트 결과 표시
    // 최적 방법 추천
}
```

## 📊 성과 측정 지표

### 기술적 성과
- **녹음 성공률**: 95% 이상 목표
- **방법별 성능**: Streamlink vs Direct 비교
- **오류 복구**: Fallback 성공률 측정
- **리소스 사용량**: CPU/메모리 최적화

### 사용자 경험
- **녹음 시작 시간**: 10초 이내
- **실시간 피드백**: 1초 이내 상태 업데이트
- **에러 메시지**: 구체적이고 actionable한 정보

## 🔧 기술적 고려사항

### Docker 환경 최적화
```yaml
# docker-compose.yml 업데이트
services:
  backend:
    environment:
      - STREAMLINK_LOGLEVEL=error
      - FFMPEG_HIDE_BANNER=1
    volumes:
      - recordings_data:/app/recordings
      - /tmp:/tmp  # 임시 파일 공간
```

### 에러 처리 및 복구
```python
class RecordingError(Exception):
    """녹음 관련 에러 체계화"""
    pass

class NetworkError(RecordingError):
    """네트워크 관련 에러"""
    pass

class StreamFormatError(RecordingError):
    """스트림 포맷 에러"""
    pass
```

### 성능 최적화
```python
# 동시 녹음 제한
MAX_CONCURRENT_RECORDINGS = 10

# 메모리 사용량 모니터링
async def monitor_memory_usage():
    # 메모리 사용량이 임계값 초과 시 새 녹음 거부
    pass
```

## 🎯 마일스톤 업데이트

- **Week 1 완료**: ✅ **시뮬레이션 → 실제 구현 교체 완료**
  - ✅ Streamlink + FFmpeg 통합
  - ✅ CBS 라디오 방송국 6개 추가
  - ✅ 테스트 스크립트 생성
  - ✅ Docker 환경 준비 완료

- **Week 2 진행 중**: 🚧 기본 테스트 및 API 완성
- **Week 3 예정**: 🚧 고급 방법들 구현 (HLS 직접, yt-dlp)
- **Week 4 예정**: 🚧 실시간 기능 통합 (WebSocket)
- **Week 5 예정**: 🚧 프론트엔드 완성
- **Week 6 예정**: 🚧 전체 시스템 통합 테스트

## 🏆 현재 달성 성과

**✅ 완전히 동작하는 기능**:
- CBS 라디오 HLS 스트림 녹음 (실제 동작)
- 자동 재시도 및 에러 처리
- 시간 제한 녹음
- 파일 크기 자동 계산
- Docker 환경에서 완전 동작

**🚀 즉시 사용 가능**:
```bash
# 1. 전체 시스템 시작
docker-compose up -d

# 2. 데이터베이스 마이그레이션 (CBS 방송국 추가)
docker-compose exec backend alembic upgrade head

# 3. 테스트 실행
python test_cbs_recording.py
```

이 로드맵을 따르면 Claude Opus와의 대화에서 제시된 모든 방법을 체계적으로 통합하여 실제로 동작하는 헤드리스 라디오 녹음 시스템을 완성할 수 있습니다.
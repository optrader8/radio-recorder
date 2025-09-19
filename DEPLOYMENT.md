# Radio Recorder 배포 및 테스트 가이드

## 🎵 CBS 라디오 녹음 시스템 운영 가이드

이 문서는 실제로 동작하는 CBS 라디오 녹음 시스템의 배포, 테스트, 운영 방법을 설명합니다.

## 🚀 빠른 시작

### 1. 시스템 요구사항

**서버 환경**:
- Ubuntu 18.04+ 또는 호환 Linux 배포판
- Docker 20.10+
- Docker Compose 1.29+
- 최소 2GB RAM, 10GB 저장공간

**네트워크**:
- 인터넷 연결 (CBS 스트림 접속용)
- 포트 80, 443, 8000, 3000 사용 가능

### 2. 설치 및 실행

```bash
# 1. 저장소 클론
git clone <repository-url>
cd radio-recorder

# 2. 환경 설정
cp .env.example .env
# .env 파일에서 SECRET_KEY 등 필수 값 설정

# 3. Docker 서비스 시작
docker-compose up -d

# 4. 데이터베이스 초기화 및 CBS 방송국 추가
docker-compose exec backend alembic upgrade head

# 5. 서비스 상태 확인
docker-compose ps
```

### 3. 접속 확인

- **프론트엔드**: http://localhost
- **API 문서**: http://localhost:8000/docs
- **백엔드 API**: http://localhost:8000

## 🧪 테스트 가이드

### 기본 테스트 (권장)

```bash
# CBS 스트림 테스트 실행
python test_cbs_recording.py
```

**예상 출력**:
```
🎵 CBS Radio Recording Test
==================================================
✅ Streamlink installed: streamlink 5.0.0

📡 Testing stream availability...
------------------------------
Testing CBS 음악FM...
  ✅ CBS 음악FM - Stream available
     Direct URL: https://m-aac.cbs.co.kr/mweb_cbs939/_definst_/cbs939...

🎙️ Testing recording functionality...
----------------------------------------
Testing 30s recording of CBS 음악FM...
  ✅ CBS 음악FM - Recording successful!
     File: test_CBS_음악FM_20240919_143022.mp3
     Size: 242,816 bytes

🎉 CBS radio recording implementation is working!
   Ready for production use.
```

### Docker 환경 테스트

```bash
# 컨테이너 내부에서 테스트
docker-compose exec backend python -c "
import asyncio
from app.services.recording_engine import _record_with_streamlink
print('✅ Recording engine import successful')
"

# Streamlink 설치 확인
docker-compose exec backend streamlink --version
```

### API 테스트

```bash
# 헬스체크
curl http://localhost:8000/api/v1/health

# CBS 방송국 목록 확인 (인증 필요시 토큰 추가)
curl http://localhost:8000/api/v1/stations

# 녹음 시작 테스트 (실제 API 구현 후)
curl -X POST http://localhost:8000/api/v1/recordings \
  -H "Content-Type: application/json" \
  -d '{"station_id": "cbs-music-fm", "duration_seconds": 30}'
```

## 🔧 트러블슈팅

### 일반적인 문제들

#### 1. Streamlink 관련 오류

**문제**: `streamlink: command not found`
```bash
# 해결: 컨테이너 재빌드
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d
```

**문제**: CBS 스트림 접속 불가
```bash
# 해결: 수동 테스트
docker-compose exec backend streamlink \
  "https://m-aac.cbs.co.kr/mweb_cbs939/_definst_/cbs939.stream/chunklist.m3u8" \
  best --stream-url
```

#### 2. 데이터베이스 관련

**문제**: 마이그레이션 실패
```bash
# 해결: 수동 마이그레이션
docker-compose exec backend alembic current
docker-compose exec backend alembic upgrade head
```

**문제**: CBS 방송국 데이터 없음
```bash
# 확인
docker-compose exec postgres psql -U radio_user -d radio_recorder \
  -c "SELECT name, stream_url FROM radio_stations WHERE name LIKE 'CBS%';"

# 수동 추가 (필요시)
docker-compose exec backend alembic upgrade head
```

#### 3. 네트워크 관련

**문제**: 컨테이너 간 통신 실패
```bash
# 네트워크 상태 확인
docker network ls
docker network inspect radio-recorder_radio-network

# 해결: 네트워크 재생성
docker-compose down
docker-compose up -d
```

### 로그 확인

```bash
# 전체 서비스 로그
docker-compose logs

# 특정 서비스 로그
docker-compose logs backend
docker-compose logs celery-worker

# 실시간 로그 추적
docker-compose logs -f backend
```

## 📊 모니터링

### 시스템 상태 확인

```bash
# 컨테이너 상태
docker-compose ps

# 리소스 사용량
docker stats

# 디스크 사용량 (녹음 파일)
docker-compose exec backend du -sh /app/recordings
```

### 녹음 상태 확인

```bash
# 활성 녹음 프로세스
docker-compose exec backend ps aux | grep streamlink

# 녹음 파일 확인
docker-compose exec backend ls -la /app/recordings
```

## 🛡️ 보안 고려사항

### 프로덕션 환경

```bash
# 1. .env 파일 보안 설정
chmod 600 .env

# 2. SECRET_KEY 강화
# 최소 50자 이상의 무작위 문자열 사용

# 3. 데이터베이스 비밀번호 변경
# POSTGRES_PASSWORD를 강한 비밀번호로 변경

# 4. 방화벽 설정
ufw allow 80
ufw allow 443
ufw deny 8000  # 직접 접근 차단 (nginx를 통해서만)
```

### SSL/TLS 설정

```bash
# Let's Encrypt 인증서 (예시)
# docker/nginx/ 폴더에 SSL 설정 추가
# nginx.conf에서 HTTPS 리다이렉트 설정
```

## 🔄 업데이트 및 백업

### 시스템 업데이트

```bash
# 1. 백업 생성
docker-compose exec postgres pg_dump -U radio_user radio_recorder > backup.sql

# 2. 새 버전 배포
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 3. 마이그레이션 실행
docker-compose exec backend alembic upgrade head
```

### 정기 백업

```bash
#!/bin/bash
# backup.sh - 정기 백업 스크립트
DATE=$(date +%Y%m%d_%H%M%S)

# 데이터베이스 백업
docker-compose exec postgres pg_dump -U radio_user radio_recorder > "db_backup_$DATE.sql"

# 녹음 파일 백업 (선택사항)
docker-compose exec backend tar -czf "recordings_backup_$DATE.tar.gz" /app/recordings

# 7일 이상 된 백업 파일 삭제
find . -name "db_backup_*.sql" -mtime +7 -delete
find . -name "recordings_backup_*.tar.gz" -mtime +7 -delete
```

```bash
# crontab에 등록 (매일 새벽 2시)
0 2 * * * /path/to/radio-recorder/backup.sh
```

## 📞 지원 및 문의

**시스템 문제 발생시**:
1. 로그 확인: `docker-compose logs`
2. 테스트 실행: `python test_cbs_recording.py`
3. 컨테이너 재시작: `docker-compose restart`
4. 전체 재배포: `docker-compose down && docker-compose up -d`

**CBS 스트림 관련 문제**:
- CBS 방송국 공식 웹사이트에서 스트림 URL 변경 여부 확인
- `test_cbs_recording.py`로 개별 스트림 테스트

이 가이드를 통해 CBS 라디오 녹음 시스템을 안정적으로 운영할 수 있습니다.
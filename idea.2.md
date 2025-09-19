서버 환경에서 사운드카드 없이 인터넷 방송을 녹음하는 것은 흔한 요구사항입니다. 몇 가지 검증된 방법을 소개하겠습니다.

## 1. **Streamlink + FFmpeg 조합 (추천)**

가장 안정적이고 범용적인 방법입니다:

```python
import subprocess
import os
from datetime import datetime

def record_stream_with_streamlink(stream_url, duration_seconds=3600):
    """
    Streamlink로 스트림을 추출하고 FFmpeg으로 녹음
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"recording_{timestamp}.mp3"
    
    # Streamlink로 best quality 스트림 URL 추출
    streamlink_cmd = [
        "streamlink", 
        stream_url, 
        "best",
        "--stream-url"
    ]
    
    try:
        # 스트림 URL 가져오기
        result = subprocess.run(streamlink_cmd, capture_output=True, text=True)
        stream_direct_url = result.stdout.strip()
        
        # FFmpeg로 녹음
        ffmpeg_cmd = [
            "ffmpeg",
            "-i", stream_direct_url,
            "-t", str(duration_seconds),
            "-acodec", "libmp3lame",
            "-ab", "128k",
            "-f", "mp3",
            output_file
        ]
        
        subprocess.run(ffmpeg_cmd)
        return output_file
        
    except Exception as e:
        print(f"Error: {e}")
        return None
```

## 2. **직접 HLS/DASH 스트림 처리**

HTTP 스트리밍 프로토콜을 직접 처리하는 방법:

```python
import requests
import m3u8
import concurrent.futures
from urllib.parse import urljoin

class HLSRecorder:
    def __init__(self, m3u8_url):
        self.m3u8_url = m3u8_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
    
    def download_segment(self, segment_url):
        """개별 TS 세그먼트 다운로드"""
        try:
            response = self.session.get(segment_url, timeout=10)
            if response.status_code == 200:
                return response.content
        except Exception as e:
            print(f"Segment download failed: {e}")
        return None
    
    def record(self, output_file, duration_seconds=3600):
        """HLS 스트림 녹음"""
        segments_data = []
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < duration_seconds:
            # m3u8 플레이리스트 파싱
            playlist = m3u8.load(self.m3u8_url)
            
            # 새로운 세그먼트만 처리
            for segment in playlist.segments:
                segment_url = urljoin(self.m3u8_url, segment.uri)
                data = self.download_segment(segment_url)
                if data:
                    segments_data.append(data)
            
            # 라이브 스트림의 경우 잠시 대기
            if playlist.is_variant:
                time.sleep(playlist.target_duration or 5)
        
        # 모든 세그먼트를 하나의 파일로 결합
        with open(output_file, 'wb') as f:
            for data in segments_data:
                f.write(data)
        
        # FFmpeg로 변환 (선택사항)
        self.convert_to_mp3(output_file)
    
    def convert_to_mp3(self, ts_file):
        """TS 파일을 MP3로 변환"""
        mp3_file = ts_file.replace('.ts', '.mp3')
        subprocess.run([
            'ffmpeg', '-i', ts_file,
            '-acodec', 'libmp3lame',
            '-ab', '128k',
            mp3_file
        ])
        os.remove(ts_file)  # 원본 TS 파일 삭제
```

## 3. **YouTube/Twitch 등 특정 플랫폼용 라이브러리**

```python
import yt_dlp
import threading
import signal

class StreamRecorder:
    def __init__(self):
        self.recording = False
        
    def record_youtube_live(self, url, output_path="recording.mp3"):
        """YouTube Live 스트림 녹음"""
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path.replace('.mp3', '.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
            'live_from_start': True,  # 처음부터 녹음
            'wait_for_video': True,   # 라이브 시작 대기
            'quiet': False,
            'no_warnings': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                self.recording = True
                ydl.download([url])
            except KeyboardInterrupt:
                print("Recording stopped by user")
            except Exception as e:
                print(f"Error: {e}")
            finally:
                self.recording = False
```

## 4. **비동기 처리를 활용한 고급 구현**

```python
import asyncio
import aiohttp
import aiofiles

class AsyncStreamRecorder:
    def __init__(self, buffer_size=1024*1024):  # 1MB buffer
        self.buffer_size = buffer_size
        self.recording = False
        
    async def record_stream(self, url, output_file, duration=3600):
        """비동기 스트림 녹음"""
        timeout = aiohttp.ClientTimeout(total=duration)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                async with aiofiles.open(output_file, 'wb') as f:
                    self.recording = True
                    start_time = asyncio.get_event_loop().time()
                    
                    async for chunk in response.content.iter_chunked(self.buffer_size):
                        if not self.recording:
                            break
                        
                        await f.write(chunk)
                        
                        # 지정된 시간 체크
                        if asyncio.get_event_loop().time() - start_time > duration:
                            break
                    
                    self.recording = False
    
    def stop_recording(self):
        """녹음 중지"""
        self.recording = False

# 사용 예시
async def main():
    recorder = AsyncStreamRecorder()
    
    # 여러 스트림 동시 녹음
    tasks = [
        recorder.record_stream("http://stream1.example.com", "output1.mp3"),
        recorder.record_stream("http://stream2.example.com", "output2.mp3"),
    ]
    
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
```

## 5. **Docker 컨테이너를 활용한 격리 환경**

서버 환경에서는 Docker를 활용하면 더 안정적입니다:

```dockerfile
# Dockerfile
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN pip install streamlink yt-dlp requests m3u8 aiohttp aiofiles

COPY recorder.py /app/
WORKDIR /app

CMD ["python", "recorder.py"]
```

## 주요 고려사항

1. **네트워크 안정성**: 재연결 로직 구현 필요
2. **저장 공간 관리**: 장시간 녹음 시 디스크 용량 모니터링
3. **메모리 관리**: 스트리밍 방식으로 처리하여 메모리 오버플로우 방지
4. **에러 핸들링**: 네트워크 끊김, 스트림 종료 등 예외 처리
5. **법적 이슈**: 저작권 및 이용약관 확인 필수

가장 추천하는 방법은 Streamlink + FFmpeg 조합입니다. 대부분의 스트리밍 플랫폼을 지원하고, 안정적이며, 서버 환경에서도 잘 동작합니다.
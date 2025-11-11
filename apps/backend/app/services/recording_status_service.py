"""
Recording status service for managing real-time recording sessions
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid
import asyncio
import os

logger = logging.getLogger(__name__)


class RecordingStatus(str, Enum):
    """Recording status enumeration"""
    PENDING = "pending"
    BUFFERING = "buffering"
    RECORDING = "recording"
    PAUSED = "paused"
    STOPPING = "stopping"
    COMPLETED = "completed"
    ERROR = "error"


class RecordingSession:
    """Represents an active recording session"""

    def __init__(
        self,
        session_id: str,
        user_id: str,
        station_id: str,
        station_name: str,
        title: str,
        file_path: str,
    ):
        self.session_id = session_id
        self.user_id = user_id
        self.station_id = station_id
        self.station_name = station_name
        self.title = title
        self.file_path = file_path
        self.status = RecordingStatus.PENDING
        self.duration_seconds: float = 0.0
        self.file_size_bytes: int = 0
        self.bitrate: int = 128  # kbps
        self.sample_rate: int = 44100  # Hz
        self.format: str = "mp3"
        self.skip_ads: bool = False
        self.started_at: Optional[datetime] = None
        self.paused_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.total_paused_seconds: float = 0.0
        self.error_message: Optional[str] = None
        self.process_id: Optional[str] = None
        self.metadata: Dict[str, Any] = {}

    def get_elapsed_seconds(self) -> float:
        """Get total elapsed recording time in seconds"""
        if not self.started_at:
            return 0.0

        end_time = self.completed_at or datetime.utcnow()
        elapsed = (end_time - self.started_at).total_seconds()
        return max(0.0, elapsed - self.total_paused_seconds)

    def get_bitrate_quality(self) -> str:
        """Get quality description for bitrate"""
        if self.bitrate >= 320:
            return "lossless"
        elif self.bitrate >= 256:
            return "high"
        elif self.bitrate >= 128:
            return "medium"
        else:
            return "low"

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "station_id": self.station_id,
            "station_name": self.station_name,
            "title": self.title,
            "file_path": self.file_path,
            "status": self.status.value,
            "duration_seconds": self.duration_seconds,
            "file_size_bytes": self.file_size_bytes,
            "file_size_mb": round(self.file_size_bytes / (1024 * 1024), 2),
            "bitrate": self.bitrate,
            "sample_rate": self.sample_rate,
            "format": self.format,
            "skip_ads": self.skip_ads,
            "quality": self.get_bitrate_quality(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "paused_at": self.paused_at.isoformat() if self.paused_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "elapsed_seconds": self.get_elapsed_seconds(),
            "total_paused_seconds": self.total_paused_seconds,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }


class RecordingStatusService:
    """Service for managing recording sessions"""

    def __init__(self):
        # Format: {user_id: {session_id: RecordingSession}}
        self.sessions: Dict[str, Dict[str, RecordingSession]] = {}
        self._lock = asyncio.Lock()

    async def create_session(
        self,
        user_id: str,
        station_id: str,
        station_name: str,
        title: str,
        file_path: str,
        skip_ads: bool = False,
        bitrate: int = 128,
        sample_rate: int = 44100,
        format: str = "mp3",
    ) -> RecordingSession:
        """Create a new recording session"""
        async with self._lock:
            if user_id not in self.sessions:
                self.sessions[user_id] = {}

            session_id = str(uuid.uuid4())
            session = RecordingSession(
                session_id=session_id,
                user_id=user_id,
                station_id=station_id,
                station_name=station_name,
                title=title,
                file_path=file_path,
            )
            session.skip_ads = skip_ads
            session.bitrate = bitrate
            session.sample_rate = sample_rate
            session.format = format

            self.sessions[user_id][session_id] = session
            logger.info(f"Recording session created: {session_id} for user {user_id}")
            return session

    async def get_session(self, user_id: str, session_id: str) -> Optional[RecordingSession]:
        """Get a recording session"""
        return self.sessions.get(user_id, {}).get(session_id)

    async def list_sessions(self, user_id: str) -> list[RecordingSession]:
        """List all recording sessions for a user"""
        return list(self.sessions.get(user_id, {}).values())

    async def list_active_sessions(self, user_id: str) -> list[RecordingSession]:
        """List all active recording sessions for a user"""
        sessions = await self.list_sessions(user_id)
        return [s for s in sessions if s.status in [RecordingStatus.RECORDING, RecordingStatus.PAUSED, RecordingStatus.BUFFERING]]

    async def start_recording(self, user_id: str, session_id: str, process_id: str) -> Optional[RecordingSession]:
        """Start recording for a session"""
        async with self._lock:
            session = await self.get_session(user_id, session_id)
            if session:
                session.status = RecordingStatus.RECORDING
                session.started_at = datetime.utcnow()
                session.process_id = process_id
                logger.info(f"Recording started: {session_id}")
                return session
        return None

    async def pause_recording(self, user_id: str, session_id: str) -> Optional[RecordingSession]:
        """Pause recording for a session"""
        async with self._lock:
            session = await self.get_session(user_id, session_id)
            if session and session.status == RecordingStatus.RECORDING:
                session.status = RecordingStatus.PAUSED
                session.paused_at = datetime.utcnow()
                logger.info(f"Recording paused: {session_id}")
                return session
        return None

    async def resume_recording(self, user_id: str, session_id: str) -> Optional[RecordingSession]:
        """Resume recording for a session"""
        async with self._lock:
            session = await self.get_session(user_id, session_id)
            if session and session.status == RecordingStatus.PAUSED:
                if session.paused_at:
                    pause_duration = (datetime.utcnow() - session.paused_at).total_seconds()
                    session.total_paused_seconds += pause_duration
                session.status = RecordingStatus.RECORDING
                session.paused_at = None
                logger.info(f"Recording resumed: {session_id}")
                return session
        return None

    async def stop_recording(self, user_id: str, session_id: str) -> Optional[RecordingSession]:
        """Stop recording for a session"""
        async with self._lock:
            session = await self.get_session(user_id, session_id)
            if session:
                if session.paused_at:
                    pause_duration = (datetime.utcnow() - session.paused_at).total_seconds()
                    session.total_paused_seconds += pause_duration
                session.status = RecordingStatus.STOPPING
                logger.info(f"Recording stopping: {session_id}")
                return session
        return None

    async def complete_recording(
        self,
        user_id: str,
        session_id: str,
        duration_seconds: float,
        file_size_bytes: int = 0,
    ) -> Optional[RecordingSession]:
        """Mark recording as completed"""
        async with self._lock:
            session = await self.get_session(user_id, session_id)
            if session:
                session.status = RecordingStatus.COMPLETED
                session.duration_seconds = duration_seconds
                session.completed_at = datetime.utcnow()

                # Update file size from actual file if available
                if os.path.exists(session.file_path):
                    session.file_size_bytes = os.path.getsize(session.file_path)
                else:
                    session.file_size_bytes = file_size_bytes

                logger.info(f"Recording completed: {session_id}")
                return session
        return None

    async def set_error(self, user_id: str, session_id: str, error_message: str) -> Optional[RecordingSession]:
        """Set error status for a session"""
        async with self._lock:
            session = await self.get_session(user_id, session_id)
            if session:
                session.status = RecordingStatus.ERROR
                session.error_message = error_message
                logger.error(f"Recording error for session {session_id}: {error_message}")
                return session
        return None

    async def update_file_size(self, user_id: str, session_id: str, file_size_bytes: int) -> Optional[RecordingSession]:
        """Update file size for a session"""
        async with self._lock:
            session = await self.get_session(user_id, session_id)
            if session:
                session.file_size_bytes = file_size_bytes
                return session
        return None

    async def delete_session(self, user_id: str, session_id: str) -> bool:
        """Delete a recording session"""
        async with self._lock:
            if user_id in self.sessions and session_id in self.sessions[user_id]:
                del self.sessions[user_id][session_id]
                if not self.sessions[user_id]:
                    del self.sessions[user_id]
                logger.info(f"Recording session deleted: {session_id}")
                return True
        return False

    async def cleanup_old_sessions(self, user_id: str, max_age_minutes: int = 60) -> int:
        """Clean up old completed/error sessions for a user"""
        async with self._lock:
            now = datetime.utcnow()
            user_sessions = self.sessions.get(user_id, {})
            sessions_to_delete = []

            for session_id, session in user_sessions.items():
                if session.status in [RecordingStatus.COMPLETED, RecordingStatus.ERROR]:
                    if session.completed_at:
                        age_minutes = (now - session.completed_at).total_seconds() / 60
                        if age_minutes > max_age_minutes:
                            sessions_to_delete.append(session_id)

            for session_id in sessions_to_delete:
                del self.sessions[user_id][session_id]

            if not self.sessions[user_id]:
                del self.sessions[user_id]

            logger.info(f"Cleaned up {len(sessions_to_delete)} old sessions for user {user_id}")
            return len(sessions_to_delete)


# Global instance
recording_status_service = RecordingStatusService()

"""
Playback service for managing real-time radio streaming
"""
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid
import asyncio
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class PlaybackStatus(str, Enum):
    """Playback status enumeration"""
    IDLE = "idle"
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    BUFFERING = "buffering"
    ERROR = "error"


class PlaybackSession:
    """Represents an active playback session"""

    def __init__(self, session_id: str, user_id: str, station_id: str, station_name: str):
        self.session_id = session_id
        self.user_id = user_id
        self.station_id = station_id
        self.station_name = station_name
        self.status = PlaybackStatus.IDLE
        self.current_position: float = 0.0  # in seconds
        self.duration: Optional[float] = None
        self.bitrate: int = 128  # kbps
        self.sample_rate: int = 44100  # Hz
        self.skip_ads: bool = False
        self.volume: float = 1.0  # 0.0 to 1.0
        self.started_at: Optional[datetime] = None
        self.paused_at: Optional[datetime] = None
        self.metadata: Dict[str, Any] = {}
        self.error_message: Optional[str] = None
        self.process_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "station_id": self.station_id,
            "station_name": self.station_name,
            "status": self.status.value,
            "current_position": self.current_position,
            "duration": self.duration,
            "bitrate": self.bitrate,
            "sample_rate": self.sample_rate,
            "skip_ads": self.skip_ads,
            "volume": self.volume,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "paused_at": self.paused_at.isoformat() if self.paused_at else None,
            "metadata": self.metadata,
            "error_message": self.error_message,
        }


class PlaybackService:
    """Service for managing radio playback sessions"""

    def __init__(self):
        # Format: {user_id: {session_id: PlaybackSession}}
        self.sessions: Dict[str, Dict[str, PlaybackSession]] = {}
        self._lock = asyncio.Lock()

    async def create_session(
        self,
        user_id: str,
        station_id: str,
        station_name: str,
        skip_ads: bool = False,
        bitrate: int = 128,
        sample_rate: int = 44100,
    ) -> PlaybackSession:
        """Create a new playback session"""
        async with self._lock:
            if user_id not in self.sessions:
                self.sessions[user_id] = {}

            session_id = str(uuid.uuid4())
            session = PlaybackSession(
                session_id=session_id,
                user_id=user_id,
                station_id=station_id,
                station_name=station_name,
            )
            session.skip_ads = skip_ads
            session.bitrate = bitrate
            session.sample_rate = sample_rate

            self.sessions[user_id][session_id] = session
            logger.info(f"Playback session created: {session_id} for user {user_id}")
            return session

    async def get_session(self, user_id: str, session_id: str) -> Optional[PlaybackSession]:
        """Get a playback session"""
        return self.sessions.get(user_id, {}).get(session_id)

    async def get_active_session(self, user_id: str) -> Optional[PlaybackSession]:
        """Get the active (first playing) playback session for a user"""
        user_sessions = self.sessions.get(user_id, {})
        for session in user_sessions.values():
            if session.status in [PlaybackStatus.PLAYING, PlaybackStatus.PAUSED]:
                return session
        return None

    async def list_sessions(self, user_id: str) -> list[PlaybackSession]:
        """List all playback sessions for a user"""
        return list(self.sessions.get(user_id, {}).values())

    async def start_playback(self, user_id: str, session_id: str) -> Optional[PlaybackSession]:
        """Start playback for a session"""
        async with self._lock:
            session = await self.get_session(user_id, session_id)
            if session:
                session.status = PlaybackStatus.PLAYING
                session.started_at = datetime.utcnow()
                logger.info(f"Playback started: {session_id}")
                return session
        return None

    async def pause_playback(self, user_id: str, session_id: str) -> Optional[PlaybackSession]:
        """Pause playback for a session"""
        async with self._lock:
            session = await self.get_session(user_id, session_id)
            if session:
                session.status = PlaybackStatus.PAUSED
                session.paused_at = datetime.utcnow()
                logger.info(f"Playback paused: {session_id}")
                return session
        return None

    async def resume_playback(self, user_id: str, session_id: str) -> Optional[PlaybackSession]:
        """Resume playback for a session"""
        async with self._lock:
            session = await self.get_session(user_id, session_id)
            if session:
                session.status = PlaybackStatus.PLAYING
                session.paused_at = None
                logger.info(f"Playback resumed: {session_id}")
                return session
        return None

    async def stop_playback(self, user_id: str, session_id: str) -> Optional[PlaybackSession]:
        """Stop playback for a session"""
        async with self._lock:
            session = await self.get_session(user_id, session_id)
            if session:
                session.status = PlaybackStatus.STOPPED
                logger.info(f"Playback stopped: {session_id}")
                return session
        return None

    async def set_volume(self, user_id: str, session_id: str, volume: float) -> Optional[PlaybackSession]:
        """Set volume for a session (0.0 to 1.0)"""
        async with self._lock:
            session = await self.get_session(user_id, session_id)
            if session:
                session.volume = max(0.0, min(1.0, volume))
                logger.info(f"Volume set to {session.volume} for session {session_id}")
                return session
        return None

    async def update_position(self, user_id: str, session_id: str, position: float) -> Optional[PlaybackSession]:
        """Update current position in playback"""
        async with self._lock:
            session = await self.get_session(user_id, session_id)
            if session:
                session.current_position = position
                return session
        return None

    async def set_error(self, user_id: str, session_id: str, error_message: str) -> Optional[PlaybackSession]:
        """Set error status for a session"""
        async with self._lock:
            session = await self.get_session(user_id, session_id)
            if session:
                session.status = PlaybackStatus.ERROR
                session.error_message = error_message
                logger.error(f"Playback error for session {session_id}: {error_message}")
                return session
        return None

    async def delete_session(self, user_id: str, session_id: str) -> bool:
        """Delete a playback session"""
        async with self._lock:
            if user_id in self.sessions and session_id in self.sessions[user_id]:
                del self.sessions[user_id][session_id]
                if not self.sessions[user_id]:
                    del self.sessions[user_id]
                logger.info(f"Playback session deleted: {session_id}")
                return True
        return False

    async def cleanup_old_sessions(self, user_id: str, max_age_minutes: int = 60) -> int:
        """Clean up old stopped/error sessions for a user"""
        async with self._lock:
            now = datetime.utcnow()
            user_sessions = self.sessions.get(user_id, {})
            sessions_to_delete = []

            for session_id, session in user_sessions.items():
                if session.status in [PlaybackStatus.STOPPED, PlaybackStatus.ERROR]:
                    if session.started_at:
                        age_minutes = (now - session.started_at).total_seconds() / 60
                        if age_minutes > max_age_minutes:
                            sessions_to_delete.append(session_id)

            for session_id in sessions_to_delete:
                del self.sessions[user_id][session_id]

            if not self.sessions[user_id]:
                del self.sessions[user_id]

            logger.info(f"Cleaned up {len(sessions_to_delete)} old sessions for user {user_id}")
            return len(sessions_to_delete)


# Global instance
playback_service = PlaybackService()

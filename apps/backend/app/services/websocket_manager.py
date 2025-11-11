"""
WebSocket connection manager for real-time communication
"""
import asyncio
import logging
from typing import Dict, Set, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts"""

    def __init__(self):
        # Format: {user_id: {connection_id: websocket}}
        self.playback_connections: Dict[str, Dict[str, Any]] = {}
        self.recording_connections: Dict[str, Dict[str, Any]] = {}
        self.system_connections: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def connect_playback(self, user_id: str, connection_id: str, websocket):
        """Register a playback WebSocket connection"""
        async with self._lock:
            if user_id not in self.playback_connections:
                self.playback_connections[user_id] = {}
            self.playback_connections[user_id][connection_id] = websocket
            logger.info(f"Playback connection established: user={user_id}, connection={connection_id}")

    async def connect_recording(self, user_id: str, connection_id: str, websocket):
        """Register a recording WebSocket connection"""
        async with self._lock:
            if user_id not in self.recording_connections:
                self.recording_connections[user_id] = {}
            self.recording_connections[user_id][connection_id] = websocket
            logger.info(f"Recording connection established: user={user_id}, connection={connection_id}")

    async def connect_system(self, user_id: str, connection_id: str, websocket):
        """Register a system notifications WebSocket connection"""
        async with self._lock:
            if user_id not in self.system_connections:
                self.system_connections[user_id] = {}
            self.system_connections[user_id][connection_id] = websocket
            logger.info(f"System connection established: user={user_id}, connection={connection_id}")

    async def disconnect_playback(self, user_id: str, connection_id: str):
        """Unregister a playback WebSocket connection"""
        async with self._lock:
            if user_id in self.playback_connections:
                self.playback_connections[user_id].pop(connection_id, None)
                if not self.playback_connections[user_id]:
                    del self.playback_connections[user_id]
                logger.info(f"Playback connection closed: user={user_id}, connection={connection_id}")

    async def disconnect_recording(self, user_id: str, connection_id: str):
        """Unregister a recording WebSocket connection"""
        async with self._lock:
            if user_id in self.recording_connections:
                self.recording_connections[user_id].pop(connection_id, None)
                if not self.recording_connections[user_id]:
                    del self.recording_connections[user_id]
                logger.info(f"Recording connection closed: user={user_id}, connection={connection_id}")

    async def disconnect_system(self, user_id: str, connection_id: str):
        """Unregister a system WebSocket connection"""
        async with self._lock:
            if user_id in self.system_connections:
                self.system_connections[user_id].pop(connection_id, None)
                if not self.system_connections[user_id]:
                    del self.system_connections[user_id]
                logger.info(f"System connection closed: user={user_id}, connection={connection_id}")

    async def broadcast_playback(self, user_id: str, message: Dict[str, Any]):
        """Broadcast message to all playback connections for a user"""
        if user_id in self.playback_connections:
            disconnected = []
            for connection_id, websocket in self.playback_connections[user_id].items():
                try:
                    await websocket.send_json({
                        **message,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    logger.error(f"Error sending playback message: {e}")
                    disconnected.append(connection_id)

            # Clean up disconnected connections
            for connection_id in disconnected:
                await self.disconnect_playback(user_id, connection_id)

    async def broadcast_recording(self, user_id: str, message: Dict[str, Any]):
        """Broadcast message to all recording connections for a user"""
        if user_id in self.recording_connections:
            disconnected = []
            for connection_id, websocket in self.recording_connections[user_id].items():
                try:
                    await websocket.send_json({
                        **message,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    logger.error(f"Error sending recording message: {e}")
                    disconnected.append(connection_id)

            # Clean up disconnected connections
            for connection_id in disconnected:
                await self.disconnect_recording(user_id, connection_id)

    async def broadcast_system(self, user_id: str, message: Dict[str, Any]):
        """Broadcast message to all system connections for a user"""
        if user_id in self.system_connections:
            disconnected = []
            for connection_id, websocket in self.system_connections[user_id].items():
                try:
                    await websocket.send_json({
                        **message,
                        "timestamp": datetime.utcnow().isoformat()
                    })
                except Exception as e:
                    logger.error(f"Error sending system message: {e}")
                    disconnected.append(connection_id)

            # Clean up disconnected connections
            for connection_id in disconnected:
                await self.disconnect_system(user_id, connection_id)

    async def broadcast_all_users_playback(self, message: Dict[str, Any]):
        """Broadcast message to all playback connections across all users"""
        for user_id in list(self.playback_connections.keys()):
            await self.broadcast_playback(user_id, message)

    async def broadcast_all_users_recording(self, message: Dict[str, Any]):
        """Broadcast message to all recording connections across all users"""
        for user_id in list(self.recording_connections.keys()):
            await self.broadcast_recording(user_id, message)

    async def broadcast_all_users_system(self, message: Dict[str, Any]):
        """Broadcast message to all system connections across all users"""
        for user_id in list(self.system_connections.keys()):
            await self.broadcast_system(user_id, message)

    def get_playback_connection_count(self, user_id: str) -> int:
        """Get number of active playback connections for a user"""
        return len(self.playback_connections.get(user_id, {}))

    def get_recording_connection_count(self, user_id: str) -> int:
        """Get number of active recording connections for a user"""
        return len(self.recording_connections.get(user_id, {}))

    def get_system_connection_count(self, user_id: str) -> int:
        """Get number of active system connections for a user"""
        return len(self.system_connections.get(user_id, {}))


# Global instance
ws_manager = ConnectionManager()

"""
Event Bus for real-time webhook-based updates
Provides publisher-subscriber pattern for recording and playback events
"""
import logging
import asyncio
from typing import Callable, Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Event types"""
    # Playback events
    PLAYBACK_STARTED = "playback.started"
    PLAYBACK_PAUSED = "playback.paused"
    PLAYBACK_RESUMED = "playback.resumed"
    PLAYBACK_STOPPED = "playback.stopped"
    PLAYBACK_ERROR = "playback.error"

    # Recording events
    RECORDING_STARTED = "recording.started"
    RECORDING_PAUSED = "recording.paused"
    RECORDING_RESUMED = "recording.resumed"
    RECORDING_STOPPED = "recording.stopped"
    RECORDING_COMPLETED = "recording.completed"
    RECORDING_ERROR = "recording.error"
    RECORDING_PROGRESS = "recording.progress"

    # System events
    SYSTEM_ALERT = "system.alert"
    SYSTEM_NOTIFICATION = "system.notification"
    SYSTEM_ERROR = "system.error"


@dataclass
class Event:
    """Event object"""
    type: EventType
    user_id: str
    timestamp: datetime
    data: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": self.type.value,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
        }

    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict())


class EventBus:
    """Event bus for pub-sub messaging"""

    def __init__(self):
        # Format: {event_type: [(user_id, callback), ...]}
        self.subscribers: Dict[EventType, List[tuple[str, Callable]]] = {}
        # Event history for debugging
        self.event_history: List[Event] = []
        self.max_history = 1000
        self._lock = asyncio.Lock()

    async def subscribe(
        self,
        event_type: EventType,
        user_id: str,
        callback: Callable[[Event], Any],
    ) -> str:
        """
        Subscribe to an event type

        Args:
            event_type: Type of event to subscribe to
            user_id: User ID
            callback: Async callback function to handle events

        Returns:
            Subscription ID
        """
        async with self._lock:
            if event_type not in self.subscribers:
                self.subscribers[event_type] = []

            self.subscribers[event_type].append((user_id, callback))
            logger.info(f"Subscribed user {user_id} to {event_type.value}")

            return f"{event_type.value}:{user_id}"

    async def unsubscribe(
        self,
        event_type: EventType,
        user_id: str,
    ) -> bool:
        """Unsubscribe from an event type"""
        async with self._lock:
            if event_type not in self.subscribers:
                return False

            before = len(self.subscribers[event_type])
            self.subscribers[event_type] = [
                (uid, cb)
                for uid, cb in self.subscribers[event_type]
                if uid != user_id
            ]
            after = len(self.subscribers[event_type])

            if after == 0:
                del self.subscribers[event_type]

            if after < before:
                logger.info(f"Unsubscribed user {user_id} from {event_type.value}")
                return True

            return False

    async def publish(
        self,
        event_type: EventType,
        user_id: str,
        data: Dict[str, Any],
    ) -> None:
        """
        Publish an event

        Args:
            event_type: Type of event
            user_id: User ID
            data: Event data
        """
        event = Event(
            type=event_type,
            user_id=user_id,
            timestamp=datetime.utcnow(),
            data=data,
        )

        # Add to history
        async with self._lock:
            self.event_history.append(event)
            if len(self.event_history) > self.max_history:
                self.event_history.pop(0)

        # Notify subscribers
        await self._notify_subscribers(event)

        logger.debug(f"Published {event_type.value} for user {user_id}")

    async def _notify_subscribers(self, event: Event) -> None:
        """Notify all subscribers of an event"""
        if event.type not in self.subscribers:
            return

        tasks = []
        for user_id, callback in self.subscribers[event.type]:
            if user_id == event.user_id or user_id == "*":  # "*" = all users
                task = asyncio.create_task(self._call_callback(callback, event))
                tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    @staticmethod
    async def _call_callback(callback: Callable[[Event], Any], event: Event) -> None:
        """Call a callback safely"""
        try:
            result = callback(event)
            if asyncio.iscoroutine(result):
                await result
        except Exception as e:
            logger.error(f"Error in event callback: {e}")

    async def publish_for_all_users(
        self,
        event_type: EventType,
        data: Dict[str, Any],
    ) -> None:
        """Publish an event for all users"""
        event = Event(
            type=event_type,
            user_id="*",
            timestamp=datetime.utcnow(),
            data=data,
        )

        async with self._lock:
            self.event_history.append(event)
            if len(self.event_history) > self.max_history:
                self.event_history.pop(0)

        await self._notify_subscribers(event)

    def get_event_history(self, user_id: str, limit: int = 100) -> List[Event]:
        """Get event history for a user"""
        return [
            e for e in self.event_history[-limit:]
            if e.user_id == user_id or e.user_id == "*"
        ]

    async def clear_subscribers(self) -> None:
        """Clear all subscribers"""
        async with self._lock:
            self.subscribers.clear()


# Global instance
event_bus = EventBus()

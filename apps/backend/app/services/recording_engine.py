import asyncio
from datetime import datetime, timezone
from pathlib import Path
from threading import Thread
from typing import Optional

from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.db.types import parse_uuid
from app.models.recording import Recording

logger = get_logger(__name__)


async def _simulate_ffmpeg(recording: Recording) -> None:
    """Simulate an FFmpeg execution and update recording status."""
    await asyncio.sleep(0.1)


async def _run_recording(recording_id: str) -> str:
    async with AsyncSessionLocal() as session:
        recording = await session.get(Recording, parse_uuid(recording_id))
        if not recording:
            logger.error("Recording %s not found", recording_id)
            return "missing"

        recording.status = "recording"
        recording.started_at = datetime.now(timezone.utc)
        await session.commit()

        try:
            await _simulate_ffmpeg(recording)
            recording.status = "completed"
            recording.completed_at = datetime.now(timezone.utc)
            await session.commit()
            return "completed"
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("Recording %s failed: %s", recording_id, exc)
            recording.status = "failed"
            recording.error_message = str(exc)
            await session.commit()
            return "failed"


def run_recording_task(recording_id: str) -> str:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(_run_recording(recording_id))

    result: dict[str, str] = {}

    def runner() -> None:
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            result['value'] = new_loop.run_until_complete(_run_recording(recording_id))
        finally:
            new_loop.close()

    thread = Thread(target=runner, daemon=True)
    thread.start()
    thread.join()
    return result.get('value', 'failed')

import asyncio
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from threading import Thread
from typing import Optional

from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.db.types import parse_uuid
from app.models.recording import Recording

logger = get_logger(__name__)


async def _record_with_streamlink(recording: Recording) -> None:
    """Record stream using Streamlink + FFmpeg."""
    try:
        # Create output directory if it doesn't exist
        output_path = Path(recording.file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Build Streamlink command
        cmd = [
            "streamlink",
            recording.station.stream_url,
            "best",
            "--output", str(output_path),
            "--force",
            "--retry-streams", "5",
            "--retry-max", "10",
            "--stream-timeout", "60"
        ]

        # Add duration limit if specified
        if recording.duration_seconds and recording.duration_seconds > 0:
            cmd.extend([
                "--ffmpeg-ffmpeg", f"-t {recording.duration_seconds}"
            ])

        logger.info(f"Starting recording with command: {' '.join(cmd)}")

        # Execute Streamlink
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            logger.info(f"Recording completed successfully: {recording.id}")

            # Update file size if file exists
            if output_path.exists():
                recording.file_size = output_path.stat().st_size
                logger.info(f"Recorded file size: {recording.file_size} bytes")
        else:
            error_msg = stderr.decode() if stderr else "Unknown error"
            logger.error(f"Streamlink failed: {error_msg}")
            raise Exception(f"Streamlink recording failed: {error_msg}")

    except Exception as e:
        logger.exception(f"Recording failed for {recording.id}: {e}")
        raise


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
            await _record_with_streamlink(recording)
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

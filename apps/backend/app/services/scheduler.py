import asyncio
from datetime import datetime, timezone
from threading import Thread

from croniter import croniter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal
from app.db.types import parse_uuid
from app.models.schedule import Schedule
from app.schemas.recording import RecordingCreate

logger = get_logger(__name__)


def _next_run(cron_expression: str, base_time: datetime) -> datetime:
    iterator = croniter(cron_expression, base_time)
    return iterator.get_next(datetime)


async def dispatch_due_schedules(now: datetime | None = None) -> int:
    now = now or datetime.now(timezone.utc)
    from app.services.recordings import create_recording

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Schedule).where(
                Schedule.is_active.is_(True),
                Schedule.next_run_at.isnot(None),
                Schedule.next_run_at <= now,
            )
        )
        schedules = list(result.scalars().all())
        dispatched = 0
        for schedule in schedules:
            payload = RecordingCreate(
                station_id=parse_uuid(schedule.station_id),
                schedule_id=parse_uuid(schedule.id),
                format=schedule.format,
                bitrate=schedule.bitrate,
                sample_rate=schedule.sample_rate,
                duration_seconds=schedule.duration_minutes * 60,
            )
            recording = await create_recording(
                session,
                user_id=parse_uuid(schedule.user_id),
                recording_in=payload,
            )
            if recording:
                dispatched += 1
                schedule.next_run_at = _next_run(schedule.cron_expression, now)

        await session.commit()
        return dispatched


def run_schedule_dispatch() -> int:
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(dispatch_due_schedules())

    result: dict[str, int] = {}

    def runner() -> None:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result['value'] = loop.run_until_complete(dispatch_due_schedules())
        finally:
            loop.close()

    thread = Thread(target=runner, daemon=True)
    thread.start()
    thread.join()
    return result.get('value', 0)

from datetime import datetime, timezone
from typing import Optional, Sequence

from croniter import croniter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.types import parse_uuid
from app.models.radio_station import RadioStation
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate


async def list_schedules(
    session: AsyncSession, *, user_id, skip: int = 0, limit: int = 50
) -> Sequence[Schedule]:
    user_ref = parse_uuid(user_id)
    result = await session.execute(
        select(Schedule)
        .where(Schedule.user_id == user_ref)
        .order_by(Schedule.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_schedule(
    session: AsyncSession, *, schedule_id, user_id
) -> Optional[Schedule]:
    sched_ref = parse_uuid(schedule_id)
    result = await session.execute(select(Schedule).where(Schedule.id == sched_ref))
    schedule = result.scalars().first()
    if schedule and str(schedule.user_id) == str(parse_uuid(user_id)):
        return schedule
    return None


async def create_schedule(
    session: AsyncSession,
    *,
    user_id,
    schedule_in: ScheduleCreate,
) -> Optional[Schedule]:
    station_ref = parse_uuid(schedule_in.station_id)
    station = await session.get(RadioStation, station_ref)
    if not station:
        return None

    user_ref = parse_uuid(user_id)
    base_time = datetime.now(timezone.utc)
    schedule = Schedule(
        user_id=user_ref,
        station_id=station_ref,
        name=schedule_in.name,
        cron_expression=schedule_in.cron_expression,
        duration_minutes=schedule_in.duration_minutes,
        format=schedule_in.format or "mp3",
        bitrate=schedule_in.bitrate or 128,
        sample_rate=schedule_in.sample_rate or 44100,
        is_active=schedule_in.is_active,
        next_run_at=croniter(schedule_in.cron_expression, base_time).get_next(datetime),
    )
    session.add(schedule)
    await session.commit()
    await session.refresh(schedule)
    return schedule

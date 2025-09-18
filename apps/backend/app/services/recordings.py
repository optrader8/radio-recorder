from datetime import datetime, timezone
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.types import parse_uuid
from app.models.recording import Recording
from app.models.radio_station import RadioStation
from app.schemas.recording import RecordingCreate
from app.workers.tasks.recordings import start_recording_task


async def list_recordings(
    session: AsyncSession, *, user_id, skip: int = 0, limit: int = 50
) -> Sequence[Recording]:
    user_ref = parse_uuid(user_id)
    result = await session.execute(
        select(Recording)
        .where(Recording.user_id == user_ref)
        .order_by(Recording.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def get_recording(
    session: AsyncSession, *, recording_id, user_id
) -> Optional[Recording]:
    rec_ref = parse_uuid(recording_id)
    result = await session.execute(select(Recording).where(Recording.id == rec_ref))
    recording = result.scalars().first()
    if recording and str(recording.user_id) == str(parse_uuid(user_id)):
        return recording
    return None


async def create_recording(
    session: AsyncSession,
    *,
    user_id,
    recording_in: RecordingCreate,
) -> Optional[Recording]:
    station_ref = parse_uuid(recording_in.station_id)
    station = await session.get(RadioStation, station_ref)
    if not station:
        return None

    user_ref = parse_uuid(user_id)
    recording = Recording(
        user_id=user_ref,
        station_id=station_ref,
        schedule_id=parse_uuid(recording_in.schedule_id) if recording_in.schedule_id else None,
        title=recording_in.title,
        format=recording_in.format,
        bitrate=recording_in.bitrate,
        sample_rate=recording_in.sample_rate,
        duration_seconds=recording_in.duration_seconds,
        status="queued",
    )
    session.add(recording)
    await session.commit()
    await session.refresh(recording)
    start_recording_task.delay(str(recording.id))
    await session.refresh(recording)
    return recording

import logging
from typing import List
from uuid import UUID
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.models.radio_station import RadioStation
from app.schemas import RecordingCreate, RecordingRead
from app.services import recordings as recording_service
from app.services.recording_engine import recording_engine, RecordingConfig
from app.services.recording_status_service import recording_status_service
from app.services.websocket_manager import ws_manager
from app.core.config import settings
import os
from sqlalchemy import select

logger = logging.getLogger(__name__)

router = APIRouter()


class RecordingStartRequest(BaseModel):
    """Request model for starting a recording"""
    station_id: str
    title: str = "New Recording"
    bitrate: int = 128
    sample_rate: int = 44100
    format: str = "mp3"
    skip_ads: bool = False
    duration_minutes: int = 0  # 0 = infinite


class RecordingStatusResponse(BaseModel):
    """Response model for recording status"""
    session_id: str
    status: str
    duration_seconds: float
    file_size_bytes: int
    bitrate: int
    started_at: str = None
    elapsed_seconds: float = 0.0
    error_message: str = None


@router.get("/", response_model=List[RecordingRead])
async def list_user_recordings(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
) -> List[RecordingRead]:
    """List all recordings for current user"""
    recordings = await recording_service.list_recordings(
        session, user_id=current_user.id, skip=skip, limit=limit
    )
    return list(recordings)


@router.get("/active", response_model=dict)
async def list_active_recordings(
    current_user: User = Depends(get_current_active_user),
):
    """Get list of currently active recording sessions"""
    try:
        active_sessions = await recording_status_service.list_active_sessions(
            str(current_user.id)
        )
        return {
            "active_recordings": [s.to_dict() for s in active_sessions],
            "total": len(active_sessions),
        }
    except Exception as e:
        logger.error(f"Error getting active recordings: {e}")
        raise HTTPException(status_code=500, detail="Failed to get active recordings")


@router.post("/start", status_code=status.HTTP_201_CREATED)
async def start_recording(
    request: RecordingStartRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Start a new recording session"""
    try:
        # Validate station exists
        try:
            station_uuid = UUID(request.station_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid station ID")

        stmt = select(RadioStation).where(RadioStation.id == station_uuid)
        result = await db.execute(stmt)
        station = result.scalar_one_or_none()

        if not station:
            raise HTTPException(status_code=404, detail="Station not found")

        # Create file path
        import time
        timestamp = int(time.time())
        filename = f"{request.title.replace(' ', '_')}_{timestamp}.{request.format}"
        file_path = os.path.join(settings.STORAGE_PATH, filename)

        # Ensure storage directory exists
        os.makedirs(settings.STORAGE_PATH, exist_ok=True)

        # Create recording session
        session = await recording_status_service.create_session(
            user_id=str(current_user.id),
            station_id=request.station_id,
            station_name=station.name,
            title=request.title,
            file_path=file_path,
            skip_ads=request.skip_ads,
            bitrate=request.bitrate,
            sample_rate=request.sample_rate,
            format=request.format,
        )

        # Create recording config
        config = RecordingConfig(
            output_format=request.format,
            bitrate=request.bitrate,
            sample_rate=request.sample_rate,
            duration_minutes=request.duration_minutes,
            disable_ssl_cert_check=True,
        )

        # Start recording in background
        import asyncio
        asyncio.create_task(
            _start_recording_task(
                session.session_id,
                str(current_user.id),
                station.stream_url,
                file_path,
                config,
                request.skip_ads,
            )
        )

        # Notify WebSocket clients
        await ws_manager.broadcast_recording(str(current_user.id), {
            "type": "recording_started",
            "session_id": session.session_id,
            "data": session.to_dict(),
        })

        logger.info(
            f"Recording started: {session.session_id} for user {current_user.username}"
        )

        return {
            "session_id": session.session_id,
            "status": "started",
            "station": station.name,
            "file_path": file_path,
            "data": session.to_dict(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting recording: {e}")
        raise HTTPException(status_code=500, detail="Failed to start recording")


@router.post("/{session_id}/stop", status_code=status.HTTP_200_OK)
async def stop_recording(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Stop an active recording session"""
    try:
        session = await recording_status_service.get_session(str(current_user.id), session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Recording session not found")

        session = await recording_status_service.stop_recording(str(current_user.id), session_id)

        # The actual ffmpeg process should check this status and terminate
        # For now, we'll mark it as stopping

        await ws_manager.broadcast_recording(str(current_user.id), {
            "type": "recording_stopping",
            "session_id": session_id,
            "data": session.to_dict(),
        })

        logger.info(f"Recording stop requested: {session_id}")

        return {
            "session_id": session_id,
            "status": "stopping",
            "data": session.to_dict(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error stopping recording: {e}")
        raise HTTPException(status_code=500, detail="Failed to stop recording")


@router.post("/{session_id}/pause", status_code=status.HTTP_200_OK)
async def pause_recording(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Pause an active recording session"""
    try:
        session = await recording_status_service.get_session(str(current_user.id), session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Recording session not found")

        session = await recording_status_service.pause_recording(str(current_user.id), session_id)
        if not session:
            raise HTTPException(status_code=400, detail="Cannot pause this recording")

        await ws_manager.broadcast_recording(str(current_user.id), {
            "type": "recording_paused",
            "session_id": session_id,
            "data": session.to_dict(),
        })

        logger.info(f"Recording paused: {session_id}")

        return {
            "session_id": session_id,
            "status": "paused",
            "data": session.to_dict(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausing recording: {e}")
        raise HTTPException(status_code=500, detail="Failed to pause recording")


@router.post("/{session_id}/resume", status_code=status.HTTP_200_OK)
async def resume_recording(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Resume a paused recording session"""
    try:
        session = await recording_status_service.get_session(str(current_user.id), session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Recording session not found")

        session = await recording_status_service.resume_recording(str(current_user.id), session_id)
        if not session:
            raise HTTPException(status_code=400, detail="Cannot resume this recording")

        await ws_manager.broadcast_recording(str(current_user.id), {
            "type": "recording_resumed",
            "session_id": session_id,
            "data": session.to_dict(),
        })

        logger.info(f"Recording resumed: {session_id}")

        return {
            "session_id": session_id,
            "status": "resumed",
            "data": session.to_dict(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming recording: {e}")
        raise HTTPException(status_code=500, detail="Failed to resume recording")


@router.get("/{session_id}/status")
async def get_recording_status(
    session_id: str,
    current_user: User = Depends(get_current_active_user),
):
    """Get detailed status of a recording session"""
    try:
        session = await recording_status_service.get_session(str(current_user.id), session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Recording session not found")

        return {
            "session_id": session_id,
            "data": session.to_dict(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recording status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get recording status")


@router.post("/", response_model=RecordingRead, status_code=status.HTTP_201_CREATED)
async def create_recording_entry(
    recording_in: RecordingCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> RecordingRead:
    """Create a scheduled recording entry (doesn't start immediately)"""
    recording = await recording_service.create_recording(
        session, user_id=current_user.id, recording_in=recording_in
    )
    if recording is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Radio station not found",
        )
    return recording


@router.get("/{recording_id}", response_model=RecordingRead)
async def get_recording_details(
    recording_id: UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> RecordingRead:
    """Get details of a saved recording"""
    recording = await recording_service.get_recording(
        session, recording_id=recording_id, user_id=current_user.id
    )
    if recording is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found",
        )
    return recording


async def _start_recording_task(
    session_id: str,
    user_id: str,
    stream_url: str,
    file_path: str,
    config: RecordingConfig,
    skip_ads: bool,
):
    """Background task to handle actual recording"""
    try:
        # Mark as recording
        await recording_status_service.start_recording(user_id, session_id, "ffmpeg")

        # Execute recording
        success = await recording_engine.record_stream(
            stream_url=stream_url,
            output_file=file_path,
            config=config,
            skip_ads=skip_ads,
        )

        if success:
            # Get file info
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                duration = config.duration_minutes * 60 if config.duration_minutes > 0 else 0

                # Mark as completed
                await recording_status_service.complete_recording(
                    user_id, session_id, duration, file_size
                )

                await ws_manager.broadcast_recording(user_id, {
                    "type": "recording_completed",
                    "session_id": session_id,
                    "file_path": file_path,
                    "file_size": file_size,
                })

                logger.info(f"Recording completed: {session_id}")
            else:
                raise Exception("Output file not created")
        else:
            await recording_status_service.set_error(
                user_id, session_id, "Recording failed"
            )
            await ws_manager.broadcast_recording(user_id, {
                "type": "recording_error",
                "session_id": session_id,
                "error": "Recording failed",
            })

    except Exception as e:
        logger.error(f"Recording task error: {e}")
        await recording_status_service.set_error(user_id, session_id, str(e))
        await ws_manager.broadcast_recording(user_id, {
            "type": "recording_error",
            "session_id": session_id,
            "error": str(e),
        })

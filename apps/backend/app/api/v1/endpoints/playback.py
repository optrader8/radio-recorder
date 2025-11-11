"""
Playback endpoints for HTTP streaming and direct play
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Response, StreamingResponse
from fastapi.responses import StreamingResponse
from typing import Optional
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.models.radio_station import RadioStation
from app.core.security import get_current_user
from app.services.recording_engine import recording_engine, RecordingConfig
from app.services.playback_service import playback_service, PlaybackSession, PlaybackStatus
from app.services.websocket_manager import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/stations")
async def get_playback_stations(db: AsyncSession = Depends(get_db)):
    """Get list of available radio stations for playback"""
    try:
        from sqlalchemy import select

        stmt = select(RadioStation).where(RadioStation.is_active == True)
        result = await db.execute(stmt)
        stations = result.scalars().all()

        return {
            "stations": [
                {
                    "id": str(station.id),
                    "name": station.name,
                    "stream_url": station.stream_url,
                    "description": station.description or "",
                    "genre": station.genre or "",
                    "country": station.country or "",
                    "language": station.language or "",
                }
                for station in stations
            ],
            "total": len(stations),
        }
    except Exception as e:
        logger.error(f"Error fetching stations: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stations")


@router.get("/stream/{station_id}")
async def stream_station(
    station_id: str,
    bitrate: int = Query(128, ge=64, le=320),
    format: str = Query("mp3", regex="^(mp3|aac|ogg)$"),
    skip_ads: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    """
    Stream radio station in real-time

    Query Parameters:
    - bitrate: Audio bitrate in kbps (64-320, default 128)
    - format: Output format (mp3, aac, ogg, default mp3)
    - skip_ads: Enable ad skipping (default False)

    Returns:
        StreamingResponse with audio stream
    """
    try:
        from sqlalchemy import select
        from uuid import UUID

        # Validate station exists
        try:
            station_uuid = UUID(station_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid station ID")

        stmt = select(RadioStation).where(RadioStation.id == station_uuid)
        result = await db.execute(stmt)
        station = result.scalar_one_or_none()

        if not station:
            raise HTTPException(status_code=404, detail="Station not found")

        logger.info(f"Starting stream for station {station.name}, user {current_user.username}")

        # Create playback session
        session = await playback_service.create_session(
            user_id=str(current_user.id),
            station_id=station_id,
            station_name=station.name,
            skip_ads=skip_ads,
            bitrate=bitrate,
            sample_rate=44100,
        )

        # Notify WebSocket clients about streaming start
        await ws_manager.broadcast_playback(str(current_user.id), {
            "type": "streaming_started",
            "session_id": session.session_id,
            "station": {
                "id": station_id,
                "name": station.name,
            },
            "bitrate": bitrate,
            "format": format,
        })

        # Create stream generator
        async def stream_generator():
            """Generate audio stream from station"""
            try:
                # Create recording config for streaming
                config = RecordingConfig(
                    output_format=format,
                    bitrate=bitrate,
                    sample_rate=44100,
                    disable_ssl_cert_check=True,
                )

                # Use recording engine for streaming (without saving to file)
                # Get stream from Streamlink
                stream_data = await recording_engine.get_stream_data(
                    stream_url=station.stream_url,
                    timeout=300,  # 5 minute timeout
                    config=config,
                    skip_ads=skip_ads,
                )

                if not stream_data:
                    logger.error(f"Failed to get stream data for {station.name}")
                    await playback_service.set_error(
                        str(current_user.id),
                        session.session_id,
                        "Failed to connect to stream",
                    )
                    return

                # Mark session as playing
                await playback_service.start_playback(str(current_user.id), session.session_id, "stream")

                # Stream data in chunks
                chunk_size = 8192
                while True:
                    try:
                        # Read chunk from stream
                        if hasattr(stream_data, 'read'):
                            chunk = stream_data.read(chunk_size)
                        else:
                            chunk = await stream_data.read(chunk_size) if hasattr(stream_data, 'read') else None

                        if not chunk:
                            logger.info(f"Stream ended for {station.name}")
                            break

                        yield chunk

                        # Update position (approximate)
                        await playback_service.update_position(
                            str(current_user.id),
                            session.session_id,
                            len(chunk) / (bitrate * 1000 / 8),  # Rough estimate
                        )

                    except asyncio.CancelledError:
                        logger.info(f"Stream cancelled for {station.name}")
                        break
                    except Exception as e:
                        logger.error(f"Error streaming chunk: {e}")
                        break

            except Exception as e:
                logger.error(f"Stream error: {e}")
                await playback_service.set_error(
                    str(current_user.id),
                    session.session_id,
                    str(e),
                )
            finally:
                # Clean up and notify
                await playback_service.stop_playback(str(current_user.id), session.session_id)
                await ws_manager.broadcast_playback(str(current_user.id), {
                    "type": "streaming_stopped",
                    "session_id": session.session_id,
                })

        return StreamingResponse(
            stream_generator(),
            media_type="audio/mpeg" if format == "mp3" else f"audio/{format}",
            headers={
                "Content-Disposition": f'inline; filename="{station.name}.{format}"',
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
                "X-Station-Name": station.name,
                "X-Session-Id": session.session_id,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Stream error: {e}")
        raise HTTPException(status_code=500, detail="Failed to stream station")


@router.post("/session/{session_id}/pause")
async def pause_stream(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Pause a playback session"""
    try:
        session = await playback_service.pause_playback(str(current_user.id), session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        await ws_manager.broadcast_playback(str(current_user.id), {
            "type": "session_paused",
            "session_id": session_id,
            "data": session.to_dict(),
        })

        return {"status": "paused", "session": session.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausing stream: {e}")
        raise HTTPException(status_code=500, detail="Failed to pause stream")


@router.post("/session/{session_id}/resume")
async def resume_stream(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Resume a paused playback session"""
    try:
        session = await playback_service.resume_playback(str(current_user.id), session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        await ws_manager.broadcast_playback(str(current_user.id), {
            "type": "session_resumed",
            "session_id": session_id,
            "data": session.to_dict(),
        })

        return {"status": "resumed", "session": session.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming stream: {e}")
        raise HTTPException(status_code=500, detail="Failed to resume stream")


@router.get("/session/{session_id}")
async def get_session_status(
    session_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get playback session status"""
    try:
        session = await playback_service.get_session(str(current_user.id), session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        return {"session": session.to_dict()}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session status")


@router.get("/sessions")
async def list_sessions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all playback sessions for current user"""
    try:
        sessions = await playback_service.list_sessions(str(current_user.id))
        return {
            "sessions": [s.to_dict() for s in sessions],
            "total": len(sessions),
        }
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to list sessions")

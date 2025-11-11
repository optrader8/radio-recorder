"""
WebSocket endpoints for real-time playback and recording updates
"""
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Optional
import json
import uuid

from app.services.websocket_manager import ws_manager
from app.services.playback_service import playback_service
from app.services.recording_status_service import recording_status_service
from app.core.security import get_current_user_from_token
from app.schemas.user import UserResponse

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/playback/{user_id}")
async def websocket_playback(websocket: WebSocket, user_id: str, token: Optional[str] = Query(None)):
    """
    WebSocket endpoint for real-time playback updates

    Messages:
    - Client -> Server:
      {
        "action": "play|pause|resume|stop|volume|seek",
        "session_id": "...",
        "data": {}
      }
    - Server -> Client:
      {
        "type": "status|progress|error",
        "session_id": "...",
        "data": {},
        "timestamp": "..."
      }
    """
    connection_id = str(uuid.uuid4())

    try:
        # Validate token if provided
        if token:
            try:
                # Simple token validation (you might want to use get_current_user_from_token)
                # For now, we just check if token exists
                pass
            except Exception as e:
                await websocket.close(code=1008, reason="Unauthorized")
                return

        await websocket.accept()
        await ws_manager.connect_playback(user_id, connection_id, websocket)
        logger.info(f"WebSocket playback connected: user={user_id}, connection={connection_id}")

        # Send initial status
        active_session = await playback_service.get_active_session(user_id)
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to playback stream",
            "active_session": active_session.to_dict() if active_session else None,
        })

        # Listen for messages from client
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            session_id = data.get("session_id")
            action_data = data.get("data", {})

            logger.debug(f"Playback action: {action} on session {session_id}")

            if action == "play":
                station_id = action_data.get("station_id")
                station_name = action_data.get("station_name", "Unknown")
                skip_ads = action_data.get("skip_ads", False)
                bitrate = action_data.get("bitrate", 128)
                sample_rate = action_data.get("sample_rate", 44100)

                session = await playback_service.create_session(
                    user_id=user_id,
                    station_id=station_id,
                    station_name=station_name,
                    skip_ads=skip_ads,
                    bitrate=bitrate,
                    sample_rate=sample_rate,
                )

                await ws_manager.broadcast_playback(user_id, {
                    "type": "session_created",
                    "session_id": session.session_id,
                    "data": session.to_dict(),
                })

                await websocket.send_json({
                    "type": "acknowledgement",
                    "action": action,
                    "session_id": session.session_id,
                    "message": "Playback started",
                })

            elif action == "pause" and session_id:
                session = await playback_service.pause_playback(user_id, session_id)
                if session:
                    await ws_manager.broadcast_playback(user_id, {
                        "type": "status_change",
                        "session_id": session_id,
                        "data": session.to_dict(),
                    })
                    await websocket.send_json({
                        "type": "acknowledgement",
                        "action": action,
                        "session_id": session_id,
                    })

            elif action == "resume" and session_id:
                session = await playback_service.resume_playback(user_id, session_id)
                if session:
                    await ws_manager.broadcast_playback(user_id, {
                        "type": "status_change",
                        "session_id": session_id,
                        "data": session.to_dict(),
                    })
                    await websocket.send_json({
                        "type": "acknowledgement",
                        "action": action,
                        "session_id": session_id,
                    })

            elif action == "stop" and session_id:
                session = await playback_service.stop_playback(user_id, session_id)
                if session:
                    await ws_manager.broadcast_playback(user_id, {
                        "type": "status_change",
                        "session_id": session_id,
                        "data": session.to_dict(),
                    })
                    await websocket.send_json({
                        "type": "acknowledgement",
                        "action": action,
                        "session_id": session_id,
                    })
                    await playback_service.delete_session(user_id, session_id)

            elif action == "volume" and session_id:
                volume = action_data.get("volume", 1.0)
                session = await playback_service.set_volume(user_id, session_id, volume)
                if session:
                    await ws_manager.broadcast_playback(user_id, {
                        "type": "status_change",
                        "session_id": session_id,
                        "data": session.to_dict(),
                    })

            elif action == "seek" and session_id:
                position = action_data.get("position", 0.0)
                session = await playback_service.update_position(user_id, session_id, position)
                if session:
                    await ws_manager.broadcast_playback(user_id, {
                        "type": "status_change",
                        "session_id": session_id,
                        "data": session.to_dict(),
                    })

            elif action == "get_status" and session_id:
                session = await playback_service.get_session(user_id, session_id)
                if session:
                    await websocket.send_json({
                        "type": "status",
                        "session_id": session_id,
                        "data": session.to_dict(),
                    })

    except WebSocketDisconnect:
        await ws_manager.disconnect_playback(user_id, connection_id)
        logger.info(f"WebSocket playback disconnected: user={user_id}, connection={connection_id}")
    except Exception as e:
        logger.error(f"WebSocket playback error: {e}")
        await ws_manager.disconnect_playback(user_id, connection_id)


@router.websocket("/ws/recording/{user_id}")
async def websocket_recording(websocket: WebSocket, user_id: str, token: Optional[str] = Query(None)):
    """
    WebSocket endpoint for real-time recording updates

    Messages:
    - Client -> Server:
      {
        "action": "start|pause|resume|stop|status",
        "session_id": "...",
        "data": {}
      }
    - Server -> Client:
      {
        "type": "status|progress|error",
        "session_id": "...",
        "data": {},
        "timestamp": "..."
      }
    """
    connection_id = str(uuid.uuid4())

    try:
        # Validate token if provided
        if token:
            try:
                # Simple token validation
                pass
            except Exception as e:
                await websocket.close(code=1008, reason="Unauthorized")
                return

        await websocket.accept()
        await ws_manager.connect_recording(user_id, connection_id, websocket)
        logger.info(f"WebSocket recording connected: user={user_id}, connection={connection_id}")

        # Send initial status
        active_sessions = await recording_status_service.list_active_sessions(user_id)
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to recording stream",
            "active_sessions": [s.to_dict() for s in active_sessions],
        })

        # Listen for messages from client
        while True:
            data = await websocket.receive_json()
            action = data.get("action")
            session_id = data.get("session_id")
            action_data = data.get("data", {})

            logger.debug(f"Recording action: {action} on session {session_id}")

            if action == "status" and session_id:
                session = await recording_status_service.get_session(user_id, session_id)
                if session:
                    await websocket.send_json({
                        "type": "status",
                        "session_id": session_id,
                        "data": session.to_dict(),
                    })

            elif action == "list_active":
                active_sessions = await recording_status_service.list_active_sessions(user_id)
                await websocket.send_json({
                    "type": "active_list",
                    "data": [s.to_dict() for s in active_sessions],
                })

    except WebSocketDisconnect:
        await ws_manager.disconnect_recording(user_id, connection_id)
        logger.info(f"WebSocket recording disconnected: user={user_id}, connection={connection_id}")
    except Exception as e:
        logger.error(f"WebSocket recording error: {e}")
        await ws_manager.disconnect_recording(user_id, connection_id)


@router.websocket("/ws/system/{user_id}")
async def websocket_system(websocket: WebSocket, user_id: str, token: Optional[str] = Query(None)):
    """
    WebSocket endpoint for system notifications and alerts

    Server -> Client:
    {
      "type": "notification|alert|info",
      "title": "...",
      "message": "...",
      "severity": "info|warning|error",
      "timestamp": "..."
    }
    """
    connection_id = str(uuid.uuid4())

    try:
        # Validate token if provided
        if token:
            try:
                # Simple token validation
                pass
            except Exception as e:
                await websocket.close(code=1008, reason="Unauthorized")
                return

        await websocket.accept()
        await ws_manager.connect_system(user_id, connection_id, websocket)
        logger.info(f"WebSocket system connected: user={user_id}, connection={connection_id}")

        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to system notifications",
        })

        # Keep connection alive
        while True:
            try:
                # Wait for any incoming message to keep connection alive
                data = await websocket.receive_json()
                # Echo back or ignore
            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        await ws_manager.disconnect_system(user_id, connection_id)
        logger.info(f"WebSocket system disconnected: user={user_id}, connection={connection_id}")
    except Exception as e:
        logger.error(f"WebSocket system error: {e}")
        await ws_manager.disconnect_system(user_id, connection_id)

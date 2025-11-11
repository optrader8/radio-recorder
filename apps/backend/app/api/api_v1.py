from fastapi import APIRouter

from app.api.v1.endpoints import (
    recordings,
    schedules,
    files,
    health,
    auth,
    users,
    ai,
    stats,
    playback
)
from app.api.endpoints import websocket

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(playback.router, prefix="/playback", tags=["playback"])
api_router.include_router(recordings.router, prefix="/recordings", tags=["recordings"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
api_router.include_router(files.router, prefix="/files", tags=["files"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(stats.router, prefix="/stats", tags=["statistics"])

# Include WebSocket endpoints
api_router.include_router(websocket.router, tags=["websocket"])
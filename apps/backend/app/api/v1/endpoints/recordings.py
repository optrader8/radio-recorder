from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas import RecordingCreate, RecordingRead
from app.services import recordings as recording_service

router = APIRouter()


@router.get("/", response_model=List[RecordingRead])
async def list_user_recordings(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
) -> List[RecordingRead]:
    recordings = await recording_service.list_recordings(
        session, user_id=current_user.id, skip=skip, limit=limit
    )
    return list(recordings)


@router.post("/", response_model=RecordingRead, status_code=status.HTTP_201_CREATED)
async def create_recording_entry(
    recording_in: RecordingCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> RecordingRead:
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
    recording = await recording_service.get_recording(
        session, recording_id=recording_id, user_id=current_user.id
    )
    if recording is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found",
        )
    return recording

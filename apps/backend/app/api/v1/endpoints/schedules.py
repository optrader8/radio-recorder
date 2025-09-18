from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas import ScheduleCreate, ScheduleRead
from app.services import schedules as schedule_service

router = APIRouter()


@router.get("/", response_model=List[ScheduleRead])
async def list_user_schedules(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 50,
) -> List[ScheduleRead]:
    schedules = await schedule_service.list_schedules(
        session, user_id=current_user.id, skip=skip, limit=limit
    )
    return list(schedules)


@router.post("/", response_model=ScheduleRead, status_code=status.HTTP_201_CREATED)
async def create_schedule_entry(
    schedule_in: ScheduleCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> ScheduleRead:
    schedule = await schedule_service.create_schedule(
        session, user_id=current_user.id, schedule_in=schedule_in
    )
    if schedule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Radio station not found",
        )
    return schedule


@router.get("/{schedule_id}", response_model=ScheduleRead)
async def get_schedule_details(
    schedule_id: UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> ScheduleRead:
    schedule = await schedule_service.get_schedule(
        session, schedule_id=schedule_id, user_id=current_user.id
    )
    if schedule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )
    return schedule

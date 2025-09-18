from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas import UserRead
from app.services import users as user_service

router = APIRouter()


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: User = Depends(get_current_active_user)) -> UserRead:
    return current_user


@router.get("/", response_model=List[UserRead])
async def list_registered_users(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> List[UserRead]:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    users = await user_service.list_users(session, skip=skip, limit=limit)
    return list(users)


@router.get("/{user_id}", response_model=UserRead)
async def get_user_by_identifier(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db),
) -> UserRead:
    if current_user.role != "admin" and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    user = await user_service.get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user

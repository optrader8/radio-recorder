from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate
from app.db.types import parse_uuid


async def get_user_by_id(session: AsyncSession, user_id) -> Optional[User]:
    lookup_id = parse_uuid(user_id)
    result = await session.execute(select(User).where(User.id == lookup_id))
    return result.scalars().first()


async def get_user_by_username(session: AsyncSession, username: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[User]:
    result = await session.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def create_user(session: AsyncSession, user_in: UserCreate) -> User:
    user = User(
        username=user_in.username,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def authenticate_user(
    session: AsyncSession, username: str, password: str
) -> Optional[User]:
    user = await get_user_by_username(session, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


async def list_users(
    session: AsyncSession, *, skip: int = 0, limit: int = 50
) -> Sequence[User]:
    result = await session.execute(
        select(User).offset(skip).limit(limit).order_by(User.created_at.desc())
    )
    return result.scalars().all()

import asyncio
import os
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import AsyncClient

# Ensure the backend package is importable when running tests from any cwd
BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from app.db.base import Base
from app.db.session import AsyncSessionLocal, engine
from app.main import app
from app.models.radio_station import RadioStation


@pytest_asyncio.fixture(autouse=True)
async def reset_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    async with AsyncClient(app=app, base_url="http://localhost") as test_client:
        yield test_client


@pytest.fixture(scope="session", autouse=True)
def cleanup_database_file() -> None:
    yield
    asyncio.run(engine.dispose())
    db_path = BACKEND_ROOT / "test.db"
    if db_path.exists():
        db_path.unlink()


@pytest_asyncio.fixture
async def station_id() -> str:
    async with AsyncSessionLocal() as session:
        station = RadioStation(
            name="Test Station",
            stream_url="http://example.com/stream.mp3",
        )
        session.add(station)
        await session.commit()
        await session.refresh(station)
        return str(station.id)

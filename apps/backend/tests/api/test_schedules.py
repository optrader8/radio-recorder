from datetime import datetime, timezone

import pytest
from httpx import AsyncClient

from app.db.session import AsyncSessionLocal
from app.db.types import parse_uuid
from app.models.schedule import Schedule
from app.workers.tasks.schedules import dispatch_schedules_task


@pytest.mark.asyncio
async def test_create_and_list_schedules(client: AsyncClient, station_id: str):
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": "scheduler",
            "email": "scheduler@example.com",
            "password": "schedulepass123",
        },
    )

    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "scheduler", "password": "schedulepass123"},
    )
    token = login.json()["access_token"]

    create_response = await client.post(
        "/api/v1/schedules/",
        json={
            "station_id": station_id,
            "name": "Daily News",
            "cron_expression": "0 7 * * *",
            "duration_minutes": 60,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == 201
    schedule = create_response.json()
    assert schedule["name"] == "Daily News"
    assert schedule["cron_expression"] == "0 7 * * *"

    list_response = await client.get(
        "/api/v1/schedules/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200
    payload = list_response.json()
    assert len(payload) == 1
    assert payload[0]["name"] == "Daily News"

    detail_response = await client.get(
        f"/api/v1/schedules/{schedule['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == schedule["id"]


@pytest.mark.asyncio
async def test_schedule_creation_requires_valid_station(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": "badstation",
            "email": "badstation@example.com",
            "password": "badpass123",
        },
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "badstation", "password": "badpass123"},
    )
    token = login.json()["access_token"]

    response = await client.post(
        "/api/v1/schedules/",
        json={
            "station_id": "00000000-0000-0000-0000-000000000000",
            "name": "Invalid",
            "cron_expression": "* * * * *",
            "duration_minutes": 30,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_schedule_dispatch_triggers_recording(client: AsyncClient, station_id: str):
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": "planner",
            "email": "planner@example.com",
            "password": "planpass123",
        },
    )

    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "planner", "password": "planpass123"},
    )
    token = login.json()["access_token"]

    schedule_response = await client.post(
        "/api/v1/schedules/",
        json={
            "station_id": station_id,
            "name": "Frequent",
            "cron_expression": "*/5 * * * *",
            "duration_minutes": 10,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    schedule_id = schedule_response.json()["id"]

    async with AsyncSessionLocal() as session:
        schedule = await session.get(Schedule, parse_uuid(schedule_id))
        schedule.next_run_at = datetime.now(timezone.utc)
        await session.commit()

    dispatched = dispatch_schedules_task()
    assert dispatched == 1

    recordings = await client.get(
        "/api/v1/recordings/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert recordings.status_code == 200
    payload = recordings.json()
    assert len(payload) == 1
    assert payload[0]["schedule_id"] == schedule_id

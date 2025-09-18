import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_and_list_recordings(client: AsyncClient, station_id: str):
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": "recuser",
            "email": "recuser@example.com",
            "password": "strongpass123",
        },
    )

    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "recuser", "password": "strongpass123"},
    )
    token = login.json()["access_token"]

    create_response = await client.post(
        "/api/v1/recordings/",
        json={
            "station_id": station_id,
            "title": "Morning Show",
            "format": "mp3",
            "bitrate": 192,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == 201
    recording = create_response.json()
    assert recording["title"] == "Morning Show"
    assert recording["status"] == "completed"

    list_response = await client.get(
        "/api/v1/recordings/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200
    payload = list_response.json()
    assert len(payload) == 1
    assert payload[0]["title"] == "Morning Show"

    detail_response = await client.get(
        f"/api/v1/recordings/{recording['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert detail_response.status_code == 200
    assert detail_response.json()["id"] == recording["id"]


@pytest.mark.asyncio
async def test_recording_creation_requires_valid_station(
    client: AsyncClient,
):
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": "nostation",
            "email": "nostation@example.com",
            "password": "nopass123",
        },
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "nostation", "password": "nopass123"},
    )
    token = login.json()["access_token"]

    response = await client.post(
        "/api/v1/recordings/",
        json={
            "station_id": "00000000-0000-0000-0000-000000000000",
            "title": "Invalid",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 404

import pytest

from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint_alive(client: AsyncClient):
    response = await client.get("/")

    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Radio Recorder API"
    assert body["status"] == "healthy"


@pytest.mark.asyncio
async def test_basic_health_endpoint(client: AsyncClient):
    response = await client.get("/api/v1/health/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["version"] == "1.0.0"

import pytest
from httpx import AsyncClient

from app.db.session import AsyncSessionLocal
from app.services import users as user_service


@pytest.mark.asyncio
async def test_user_registration_and_login(client: AsyncClient):
    register_payload = {
        "username": "alice",
        "email": "alice@example.com",
        "password": "securepass123",
    }
    register_response = await client.post("/api/v1/auth/register", json=register_payload)
    assert register_response.status_code == 201
    data = register_response.json()
    assert data["username"] == "alice"
    assert data["email"] == "alice@example.com"

    login_response = await client.post(
        "/api/v1/auth/login",
        json={"username": "alice", "password": "securepass123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    assert token

    me_response = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert me_response.status_code == 200
    me_payload = me_response.json()
    assert me_payload["username"] == "alice"
    assert me_payload["email"] == "alice@example.com"


@pytest.mark.asyncio
async def test_duplicate_registration_rejected(client: AsyncClient):
    payload = {
        "username": "bob",
        "email": "bob@example.com",
        "password": "anotherpass123",
    }
    first = await client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    second = await client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 400
    assert second.json()["detail"] == "Username already registered"


@pytest.mark.asyncio
async def test_non_admin_cannot_list_users(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": "charlie",
            "email": "charlie@example.com",
            "password": "mypassword123",
        },
    )
    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "charlie", "password": "mypassword123"},
    )
    token = login.json()["access_token"]

    response = await client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_can_list_users(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": "admin",
            "email": "admin@example.com",
            "password": "adminpassword123",
        },
    )

    async with AsyncSessionLocal() as session:
        admin_user = await user_service.get_user_by_username(session, "admin")
        admin_user.role = "admin"
        await session.commit()

    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "admin", "password": "adminpassword123"},
    )
    token = login.json()["access_token"]

    response = await client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 1
    assert users[0]["username"] == "admin"


@pytest.mark.asyncio
async def test_admin_can_fetch_specific_user(client: AsyncClient):
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": "primary",
            "email": "primary@example.com",
            "password": "primarysecret",
        },
    )
    admin_register = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "superadmin",
            "email": "superadmin@example.com",
            "password": "supersecret",
        },
    )
    admin_data = admin_register.json()

    async with AsyncSessionLocal() as session:
        admin_user = await user_service.get_user_by_username(session, "superadmin")
        admin_user.role = "admin"
        await session.commit()

    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "superadmin", "password": "supersecret"},
    )
    token = login.json()["access_token"]

    response = await client.get(
        f"/api/v1/users/{admin_data['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == "superadmin"

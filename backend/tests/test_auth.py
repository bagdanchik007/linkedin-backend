import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    """Server antwortet korrekt auf Health-Check."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_register_erfolgreich(client: AsyncClient):
    """Neue Registrierung gibt Access- und Refresh-Token zurück."""
    response = await client.post("/auth/register", json={
        "email": "neu@devconnect.de",
        "password": "passwort123",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_doppelte_email(client: AsyncClient):
    """Registrierung mit bereits verwendeter E-Mail schlägt fehl."""
    payload = {"email": "doppelt@devconnect.de", "password": "passwort123"}
    await client.post("/auth/register", json=payload)
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_login_erfolgreich(client: AsyncClient):
    """Anmeldung mit korrekten Zugangsdaten gibt Tokens zurück."""
    await client.post("/auth/register", json={
        "email": "login@devconnect.de",
        "password": "passwort123",
    })
    response = await client.post("/auth/login", json={
        "email": "login@devconnect.de",
        "password": "passwort123",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_falsches_passwort(client: AsyncClient):
    """Anmeldung mit falschem Passwort wird abgelehnt."""
    await client.post("/auth/register", json={
        "email": "falsch@devconnect.de",
        "password": "richtiges_passwort",
    })
    response = await client.post("/auth/login", json={
        "email": "falsch@devconnect.de",
        "password": "falsches_passwort",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_unbekannte_email(client: AsyncClient):
    """Anmeldung mit nicht existierender E-Mail wird abgelehnt."""
    response = await client.post("/auth/login", json={
        "email": "nichtexistent@devconnect.de",
        "password": "passwort123",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, registered_user: dict):
    """Access Token kann mit Refresh Token erneuert werden."""
    response = await client.post("/auth/refresh", json={
        "refresh_token": registered_user["refresh_token"],
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    # Neuer Token muss sich vom alten unterscheiden
    assert data["access_token"] != registered_user["access_token"]


@pytest.mark.asyncio
async def test_refresh_token_ungueltig(client: AsyncClient):
    """Ungültiger Refresh Token wird abgelehnt."""
    response = await client.post("/auth/refresh", json={
        "refresh_token": "ungueltigertoken123",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, registered_user: dict, auth_headers: dict):
    """Nach dem Logout ist der Refresh Token ungültig."""
    response = await client.post("/auth/logout",
        json={"refresh_token": registered_user["refresh_token"]},
        headers=auth_headers,
    )
    assert response.status_code == 204

    # Refresh Token nach Logout verwenden — muss fehlschlagen
    response = await client.post("/auth/refresh", json={
        "refresh_token": registered_user["refresh_token"],
    })
    assert response.status_code == 401

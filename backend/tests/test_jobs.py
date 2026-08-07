import pytest
from httpx import AsyncClient


async def recruiter_erstellen(client: AsyncClient) -> dict:
    """Hilfsfunktion: Recruiter registrieren und Rolle setzen."""
    response = await client.post("/auth/register", json={
        "email": "recruiter@devconnect.de",
        "password": "passwort123",
    })
    tokens = response.json()

    # Rolle direkt in der DB setzen — hier vereinfacht über direkten DB-Zugriff
    # In echten Tests würde man einen Admin-Endpunkt verwenden
    from tests.conftest import session_maker_test
    from sqlalchemy import update
    from app.users.models import User

    async with session_maker_test() as db:
        await db.execute(
            update(User)
            .where(User.email == "recruiter@devconnect.de")
            .values(role="recruiter")
        )
        await db.commit()

    # Neu einloggen um frischen Token zu bekommen
    login = await client.post("/auth/login", json={
        "email": "recruiter@devconnect.de",
        "password": "passwort123",
    })
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


@pytest.mark.asyncio
async def test_stelle_erstellen(client: AsyncClient):
    """Recruiter kann eine neue Stelle erstellen."""
    headers = await recruiter_erstellen(client)
    response = await client.post("/jobs", json={
        "title": "Python Backend Entwickler",
        "description": "FastAPI und PostgreSQL Kenntnisse erforderlich",
        "company": "TechGmbH",
        "location": "Berlin",
        "skills_required": ["Python", "FastAPI", "PostgreSQL"],
    }, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Python Backend Entwickler"
    assert data["company"] == "TechGmbH"


@pytest.mark.asyncio
async def test_stelle_erstellen_ohne_recruiter_rolle(client: AsyncClient, auth_headers: dict):
    """Normaler Benutzer kann keine Stelle erstellen."""
    response = await client.post("/jobs", json={
        "title": "Entwickler gesucht",
        "company": "IrgendeinUnternehmen",
    }, headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_stellen_liste(client: AsyncClient, auth_headers: dict):
    """Liste aller aktiven Stellen abrufen."""
    response = await client.get("/jobs")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_stelle_nach_id(client: AsyncClient):
    """Eine bestimmte Stelle anhand der ID abrufen."""
    headers = await recruiter_erstellen(client)
    # Stelle erstellen
    create = await client.post("/jobs", json={
        "title": "React Entwickler",
        "company": "WebAG",
    }, headers=headers)
    job_id = create.json()["id"]

    # Stelle abrufen
    response = await client.get(f"/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["id"] == job_id


@pytest.mark.asyncio
async def test_stelle_nicht_gefunden(client: AsyncClient):
    """Nicht existierende Stelle gibt 404 zurück."""
    response = await client.get("/jobs/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_stelle_aktualisieren(client: AsyncClient):
    """Autor kann seine Stelle bearbeiten."""
    headers = await recruiter_erstellen(client)
    create = await client.post("/jobs", json={
        "title": "Junior Developer",
        "company": "StartupGmbH",
    }, headers=headers)
    job_id = create.json()["id"]

    response = await client.patch(f"/jobs/{job_id}",
        json={"title": "Senior Developer"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Senior Developer"


@pytest.mark.asyncio
async def test_stelle_loeschen(client: AsyncClient):
    """Autor kann seine Stelle löschen."""
    headers = await recruiter_erstellen(client)
    create = await client.post("/jobs", json={
        "title": "Zu löschende Stelle",
        "company": "TestGmbH",
    }, headers=headers)
    job_id = create.json()["id"]

    response = await client.delete(f"/jobs/{job_id}", headers=headers)
    assert response.status_code == 204

    # Stelle sollte nicht mehr gefunden werden
    response = await client.get(f"/jobs/{job_id}")
    assert response.status_code == 404

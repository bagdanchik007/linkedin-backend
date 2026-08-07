import pytest
from httpx import AsyncClient
from sqlalchemy import update

from app.users.models import User
from tests.conftest import session_maker_test


async def stelle_erstellen(client: AsyncClient) -> str:
    """Hilfsfunktion: Recruiter + Stelle erstellen, Job-ID zurückgeben."""
    await client.post("/auth/register", json={
        "email": "recruiter2@devconnect.de",
        "password": "passwort123",
    })
    async with session_maker_test() as db:
        await db.execute(
            update(User)
            .where(User.email == "recruiter2@devconnect.de")
            .values(role="recruiter")
        )
        await db.commit()

    login = await client.post("/auth/login", json={
        "email": "recruiter2@devconnect.de",
        "password": "passwort123",
    })
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    job = await client.post("/jobs", json={
        "title": "Python Entwickler",
        "company": "TestGmbH",
        "skills_required": ["Python"],
    }, headers=headers)

    return job.json()["id"], headers


@pytest.mark.asyncio
async def test_bewerbung_abschicken(client: AsyncClient, auth_headers: dict):
    """Benutzer kann sich auf eine Stelle bewerben."""
    job_id, _ = await stelle_erstellen(client)
    response = await client.post(f"/jobs/{job_id}/apply",
        json={"cover_note": "Ich bin sehr motiviert!"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert data["cover_note"] == "Ich bin sehr motiviert!"


@pytest.mark.asyncio
async def test_doppelte_bewerbung_verboten(client: AsyncClient, auth_headers: dict):
    """Doppelte Bewerbung auf dieselbe Stelle wird abgelehnt."""
    job_id, _ = await stelle_erstellen(client)
    await client.post(f"/jobs/{job_id}/apply",
        json={},
        headers=auth_headers,
    )
    # Zweite Bewerbung auf dieselbe Stelle
    response = await client.post(f"/jobs/{job_id}/apply",
        json={},
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_meine_bewerbungen(client: AsyncClient, auth_headers: dict):
    """Benutzer kann seine eigenen Bewerbungen abrufen."""
    job_id, _ = await stelle_erstellen(client)
    await client.post(f"/jobs/{job_id}/apply", json={}, headers=auth_headers)

    response = await client.get("/applications/my", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["job_id"] == job_id


@pytest.mark.asyncio
async def test_bewerbungsstatus_aendern(client: AsyncClient, auth_headers: dict):
    """Recruiter kann Bewerbungsstatus auf accepted oder rejected setzen."""
    job_id, recruiter_headers = await stelle_erstellen(client)
    # Benutzer bewirbt sich
    apply = await client.post(f"/jobs/{job_id}/apply", json={}, headers=auth_headers)
    application_id = apply.json()["id"]

    # Recruiter ändert Status
    response = await client.patch(f"/applications/{application_id}/status",
        json={"status": "accepted"},
        headers=recruiter_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


@pytest.mark.asyncio
async def test_status_ohne_berechtigung(client: AsyncClient, auth_headers: dict, second_auth_headers: dict):
    """Nur der Stellenautor darf den Status ändern."""
    job_id, _ = await stelle_erstellen(client)
    apply = await client.post(f"/jobs/{job_id}/apply", json={}, headers=auth_headers)
    application_id = apply.json()["id"]

    # Zweiter Benutzer versucht Status zu ändern — kein Zugriff
    response = await client.patch(f"/applications/{application_id}/status",
        json={"status": "accepted"},
        headers=second_auth_headers,
    )
    assert response.status_code == 403

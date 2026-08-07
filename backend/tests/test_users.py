import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, auth_headers: dict):
    """Aktueller Benutzer kann sein Profil abrufen."""
    response = await client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@devconnect.de"
    assert "id" in data
    assert "password" not in data  # Passwort darf nicht zurückgegeben werden


@pytest.mark.asyncio
async def test_get_me_ohne_token(client: AsyncClient):
    """Ohne Token wird der Zugriff verweigert."""
    response = await client.get("/users/me")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_profil(client: AsyncClient, auth_headers: dict):
    """Benutzer kann sein eigenes Profil abrufen — wird automatisch erstellt."""
    response = await client.get("/users/me/profile", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "skills" in data


@pytest.mark.asyncio
async def test_profil_aktualisieren(client: AsyncClient, auth_headers: dict):
    """Benutzer kann Bio, Skills und Standort aktualisieren."""
    response = await client.patch("/users/me/profile",
        json={
            "full_name": "Max Mustermann",
            "bio": "Backend-Entwickler aus Berlin",
            "location": "Berlin",
            "skills": ["Python", "FastAPI", "PostgreSQL"],
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Max Mustermann"
    assert data["location"] == "Berlin"
    assert "Python" in data["skills"]


@pytest.mark.asyncio
async def test_profil_teilweise_aktualisieren(client: AsyncClient, auth_headers: dict):
    """Nur geänderte Felder werden aktualisiert — andere bleiben unberührt."""
    # Erst vollständiges Profil anlegen
    await client.patch("/users/me/profile",
        json={"full_name": "Max", "bio": "Entwickler", "location": "München"},
        headers=auth_headers,
    )
    # Nur Bio aktualisieren
    response = await client.patch("/users/me/profile",
        json={"bio": "Senior Entwickler"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["bio"] == "Senior Entwickler"
    # Name und Standort sollen unverändert bleiben
    assert data["full_name"] == "Max"
    assert data["location"] == "München"


@pytest.mark.asyncio
async def test_profil_mit_erfahrung(client: AsyncClient, auth_headers: dict):
    """Berufserfahrung kann als JSON-Array gespeichert werden."""
    response = await client.patch("/users/me/profile",
        json={
            "experience": [
                {"title": "Junior Developer", "company": "TechGmbH", "years": 2},
                {"title": "Backend Developer", "company": "StartupAG", "years": 1},
            ]
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["experience"]) == 2
    assert data["experience"][0]["title"] == "Junior Developer"

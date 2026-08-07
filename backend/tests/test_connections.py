import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_verbindungsanfrage_senden(
    client: AsyncClient,
    auth_headers: dict,
    second_user: dict,
):
    """Benutzer kann einem anderen eine Verbindungsanfrage senden."""
    receiver_id = second_user  # second_user gibt tokens zurück, wir brauchen die ID

    # ID des zweiten Benutzers abrufen
    second_headers = {"Authorization": f"Bearer {second_user['access_token']}"}
    me = await client.get("/users/me", headers=second_headers)
    receiver_id = me.json()["id"]

    response = await client.post(
        f"/connections/request/{receiver_id}",
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_anfrage_an_sich_selbst_verboten(client: AsyncClient, auth_headers: dict):
    """Benutzer kann keine Verbindungsanfrage an sich selbst senden."""
    me = await client.get("/users/me", headers=auth_headers)
    my_id = me.json()["id"]

    response = await client.post(f"/connections/request/{my_id}", headers=auth_headers)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_anfrage_annehmen(
    client: AsyncClient,
    auth_headers: dict,
    second_user: dict,
):
    """Empfänger kann eine Verbindungsanfrage annehmen."""
    second_headers = {"Authorization": f"Bearer {second_user['access_token']}"}
    me = await client.get("/users/me", headers=second_headers)
    receiver_id = me.json()["id"]

    # Anfrage senden
    send = await client.post(f"/connections/request/{receiver_id}", headers=auth_headers)
    connection_id = send.json()["id"]

    # Anfrage annehmen
    response = await client.patch(
        f"/connections/{connection_id}/accept",
        headers=second_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "accepted"


@pytest.mark.asyncio
async def test_anfrage_ablehnen(
    client: AsyncClient,
    auth_headers: dict,
    second_user: dict,
):
    """Empfänger kann eine Verbindungsanfrage ablehnen."""
    second_headers = {"Authorization": f"Bearer {second_user['access_token']}"}
    me = await client.get("/users/me", headers=second_headers)
    receiver_id = me.json()["id"]

    send = await client.post(f"/connections/request/{receiver_id}", headers=auth_headers)
    connection_id = send.json()["id"]

    response = await client.patch(
        f"/connections/{connection_id}/reject",
        headers=second_headers,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "rejected"


@pytest.mark.asyncio
async def test_meine_verbindungen(
    client: AsyncClient,
    auth_headers: dict,
    second_user: dict,
):
    """Angenommene Verbindungen erscheinen in der Kontaktliste."""
    second_headers = {"Authorization": f"Bearer {second_user['access_token']}"}
    me = await client.get("/users/me", headers=second_headers)
    receiver_id = me.json()["id"]

    # Anfrage senden und annehmen
    send = await client.post(f"/connections/request/{receiver_id}", headers=auth_headers)
    connection_id = send.json()["id"]
    await client.patch(f"/connections/{connection_id}/accept", headers=second_headers)

    # Kontaktliste prüfen
    response = await client.get("/connections/my", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_eingehende_anfragen(
    client: AsyncClient,
    auth_headers: dict,
    second_user: dict,
):
    """Ausstehende Anfragen erscheinen in der Pending-Liste des Empfängers."""
    second_headers = {"Authorization": f"Bearer {second_user['access_token']}"}
    me = await client.get("/users/me", headers=second_headers)
    receiver_id = me.json()["id"]

    await client.post(f"/connections/request/{receiver_id}", headers=auth_headers)

    # Empfänger sieht die ausstehende Anfrage
    response = await client.get("/connections/pending", headers=second_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_verbindung_loeschen(
    client: AsyncClient,
    auth_headers: dict,
    second_user: dict,
):
    """Beteiligte können eine Verbindung löschen."""
    second_headers = {"Authorization": f"Bearer {second_user['access_token']}"}
    me = await client.get("/users/me", headers=second_headers)
    receiver_id = me.json()["id"]

    send = await client.post(f"/connections/request/{receiver_id}", headers=auth_headers)
    connection_id = send.json()["id"]
    await client.patch(f"/connections/{connection_id}/accept", headers=second_headers)

    # Verbindung löschen
    response = await client.delete(f"/connections/{connection_id}", headers=auth_headers)
    assert response.status_code == 204

    # Kontaktliste muss jetzt leer sein
    response = await client.get("/connections/my", headers=auth_headers)
    assert len(response.json()) == 0

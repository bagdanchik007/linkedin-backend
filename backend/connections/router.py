import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.connections import service
from app.connections.schemas import ConnectionResponse, UserSuggestionResponse
from app.core.database import get_db
from app.profiles.service import get_profile_by_user_id
from app.users.models import User

router = APIRouter(prefix="/connections", tags=["Connections"])


@router.post(
    "/request/{user_id}",
    response_model=ConnectionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_request(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Man kann sich nicht selbst hinzufügen
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Du kannst dir selbst keine Anfrage senden",
        )

    # Bereits existierende Verbindung prüfen
    existing = await service.get_connection(db, current_user.id, user_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verbindungsanfrage bereits gesendet",
        )

    # Auch umgekehrte Richtung prüfen
    reverse = await service.get_connection(db, user_id, current_user.id)
    if reverse:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verbindung existiert bereits",
        )

    connection = await service.send_request(db, current_user.id, user_id)

    # Celery Task: Empfänger im Hintergrund benachrichtigen
    from app.notifications.tasks import notify_connection_request
    notify_connection_request.delay(
        str(user_id),
        str(current_user.id),
        current_user.email,
    )

    return connection


@router.patch("/{connection_id}/accept", response_model=ConnectionResponse)
async def accept_request(
    connection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    connection = await service.get_connection_by_id(db, connection_id)
    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anfrage nicht gefunden")

    # Nur der Empfänger darf annehmen
    if connection.receiver_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Kein Zugriff")

    if connection.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Anfrage ist nicht mehr ausstehend",
        )

    return await service.update_connection_status(db, connection, "accepted")


@router.patch("/{connection_id}/reject", response_model=ConnectionResponse)
async def reject_request(
    connection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    connection = await service.get_connection_by_id(db, connection_id)
    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anfrage nicht gefunden")

    # Nur der Empfänger darf ablehnen
    if connection.receiver_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Kein Zugriff")

    return await service.update_connection_status(db, connection, "rejected")


@router.delete("/{connection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_connection(
    connection_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    connection = await service.get_connection_by_id(db, connection_id)
    if not connection:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Verbindung nicht gefunden")

    # Nur Beteiligte dürfen die Verbindung löschen
    if current_user.id not in (connection.requester_id, connection.receiver_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Kein Zugriff")

    await service.delete_connection(db, connection)


@router.get("/my", response_model=list[ConnectionResponse])
async def my_connections(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.get_my_connections(db, current_user.id)


@router.get("/pending", response_model=list[ConnectionResponse])
async def pending_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.get_pending_requests(db, current_user.id)


@router.get("/suggestions", response_model=list[UserSuggestionResponse])
async def suggestions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = await get_profile_by_user_id(db, current_user.id)
    user_skills = profile.skills if profile and profile.skills else []
    return await service.get_suggestions(db, current_user.id, user_skills)

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.notifications import service
from app.notifications.schemas import NotificationResponse, UnreadCountResponse
from app.users.models import User

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationResponse])
async def get_notifications(
    limit: int = Query(30, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Liste aller Benachrichtigungen des aktuellen Benutzers."""
    return await service.get_my_notifications(db, current_user.id, limit, offset)


@router.get("/unread-count", response_model=UnreadCountResponse)
async def unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Anzahl der ungelesenen Benachrichtigungen — nützlich für das Badge im Frontend."""
    count = await service.get_unread_count(db, current_user.id)
    return UnreadCountResponse(count=count)


@router.patch("/{notification_id}/read", response_model=NotificationResponse)
async def mark_read(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Eine Benachrichtigung als gelesen markieren."""
    notification = await service.get_notification_by_id(db, notification_id)
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Benachrichtigung nicht gefunden",
        )
    # Nur eigene Benachrichtigungen dürfen geändert werden
    if notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kein Zugriff",
        )
    return await service.mark_as_read(db, notification)


@router.patch("/read-all", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Alle Benachrichtigungen als gelesen markieren."""
    await service.mark_all_as_read(db, current_user.id)

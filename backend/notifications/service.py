import uuid

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.notifications.models import Notification


async def create_notification(
    db: AsyncSession,
    user_id: uuid.UUID,
    type: str,
    payload: dict | None = None,
) -> Notification:
    """Neue Benachrichtigung für einen Benutzer erstellen."""
    notification = Notification(
        user_id=user_id,
        type=type,
        payload=payload,
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification


async def get_my_notifications(
    db: AsyncSession,
    user_id: uuid.UUID,
    limit: int = 30,
    offset: int = 0,
) -> list[Notification]:
    """Alle Benachrichtigungen des Benutzers — neueste zuerst."""
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(result.scalars().all())


async def get_notification_by_id(
    db: AsyncSession,
    notification_id: uuid.UUID,
) -> Notification | None:
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    return result.scalar_one_or_none()


async def mark_as_read(
    db: AsyncSession,
    notification: Notification,
) -> Notification:
    """Eine einzelne Benachrichtigung als gelesen markieren."""
    notification.is_read = True
    await db.commit()
    await db.refresh(notification)
    return notification


async def mark_all_as_read(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> None:
    """Alle Benachrichtigungen des Benutzers als gelesen markieren."""
    await db.execute(
        update(Notification)
        .where(Notification.user_id == user_id, Notification.is_read == False)
        .values(is_read=True)
    )
    await db.commit()


async def get_unread_count(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> int:
    """Anzahl der ungelesenen Benachrichtigungen."""
    result = await db.execute(
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == user_id, Notification.is_read == False)
    )
    return result.scalar_one()

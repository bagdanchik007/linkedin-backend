import uuid
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.notifications.models import Notification


async def create_notification(db, user_id, type, payload=None):
    """Neue Benachrichtigung für einen Benutzer erstellen."""
    notification = Notification(user_id=user_id, type=type, payload=payload)
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification


async def get_my_notifications(db, user_id, limit=30, offset=0):
    """Alle Benachrichtigungen des Benutzers — neueste zuerst."""
    result = await db.execute(select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc()).limit(limit).offset(offset))
    return list(result.scalars().all())


async def get_notification_by_id(db, notification_id):
    result = await db.execute(select(Notification).where(Notification.id == notification_id))
    return result.scalar_one_or_none()


async def mark_as_read(db, notification):
    """Eine einzelne Benachrichtigung als gelesen markieren."""
    notification.is_read = True
    await db.commit()
    await db.refresh(notification)
    return notification


async def mark_all_as_read(db, user_id):
    """Alle Benachrichtigungen des Benutzers als gelesen markieren."""
    await db.execute(update(Notification).where(Notification.user_id == user_id, Notification.is_read == False).values(is_read=True))
    await db.commit()


async def get_unread_count(db, user_id):
    """Anzahl der ungelesenen Benachrichtigungen."""
    result = await db.execute(select(func.count()).select_from(Notification).where(Notification.user_id == user_id, Notification.is_read == False))
    return result.scalar_one()

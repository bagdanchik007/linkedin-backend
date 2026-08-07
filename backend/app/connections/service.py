import uuid

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.connections.models import Connection
from app.profiles.models import Profile
from app.users.models import User


async def get_connection(
    db: AsyncSession,
    requester_id: uuid.UUID,
    receiver_id: uuid.UUID,
) -> Connection | None:
    result = await db.execute(
        select(Connection).where(
            Connection.requester_id == requester_id,
            Connection.receiver_id == receiver_id,
        )
    )
    return result.scalar_one_or_none()


async def get_connection_by_id(
    db: AsyncSession, connection_id: uuid.UUID
) -> Connection | None:
    result = await db.execute(
        select(Connection).where(Connection.id == connection_id)
    )
    return result.scalar_one_or_none()


async def send_request(
    db: AsyncSession,
    requester_id: uuid.UUID,
    receiver_id: uuid.UUID,
) -> Connection:
    connection = Connection(requester_id=requester_id, receiver_id=receiver_id)
    db.add(connection)
    await db.commit()
    await db.refresh(connection)
    return connection


async def update_connection_status(
    db: AsyncSession,
    connection: Connection,
    new_status: str,
) -> Connection:
    connection.status = new_status
    await db.commit()
    await db.refresh(connection)
    return connection


async def delete_connection(db: AsyncSession, connection: Connection) -> None:
    await db.delete(connection)
    await db.commit()


async def get_my_connections(
    db: AsyncSession, user_id: uuid.UUID
) -> list[Connection]:
    # Alle angenommenen Verbindungen des Benutzers
    result = await db.execute(
        select(Connection).where(
            or_(
                Connection.requester_id == user_id,
                Connection.receiver_id == user_id,
            ),
            Connection.status == "accepted",
        )
    )
    return list(result.scalars().all())


async def get_pending_requests(
    db: AsyncSession, user_id: uuid.UUID
) -> list[Connection]:
    # Eingehende Anfragen die noch ausstehen
    result = await db.execute(
        select(Connection).where(
            Connection.receiver_id == user_id,
            Connection.status == "pending",
        )
    )
    return list(result.scalars().all())


async def get_suggestions(
    db: AsyncSession,
    current_user_id: uuid.UUID,
    user_skills: list[str],
    limit: int = 10,
) -> list[dict]:
    """
    Empfehlungen basierend auf gemeinsamen Skills.
    Benutzer mit denen man noch nicht verbunden ist werden vorgeschlagen.
    """
    # IDs aller bereits verbundenen Benutzer holen
    connections_result = await db.execute(
        select(Connection).where(
            or_(
                Connection.requester_id == current_user_id,
                Connection.receiver_id == current_user_id,
            )
        )
    )
    connections = connections_result.scalars().all()

    # Alle bekannten User-IDs sammeln (sich selbst + alle Verbindungen)
    excluded_ids = {current_user_id}
    for conn in connections:
        excluded_ids.add(conn.requester_id)
        excluded_ids.add(conn.receiver_id)

    # Profile suchen die nicht ausgeschlossen sind
    query = (
        select(Profile, User)
        .join(User, User.id == Profile.user_id)
        .where(Profile.user_id.not_in(excluded_ids))
    )

    # Skills-Filter: gemeinsame Skills bevorzugen
    if user_skills:
        from sqlalchemy import or_ as sql_or
        skill_conditions = [Profile.skills.any(skill) for skill in user_skills]
        query = query.where(sql_or(*skill_conditions))

    query = query.limit(limit)
    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "id": profile.user_id,
            "email": user.email,
            "full_name": profile.full_name,
            "skills": profile.skills,
        }
        for profile, user in rows
    ]

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.applications.models import Application
from app.applications.schemas import ApplicationCreateRequest, ApplicationStatusUpdate


async def get_application_by_id(
    db: AsyncSession, application_id: uuid.UUID
) -> Application | None:
    result = await db.execute(
        select(Application).where(Application.id == application_id)
    )
    return result.scalar_one_or_none()


async def get_application_by_user_and_job(
    db: AsyncSession, user_id: uuid.UUID, job_id: uuid.UUID
) -> Application | None:
    result = await db.execute(
        select(Application).where(
            Application.user_id == user_id,
            Application.job_id == job_id,
        )
    )
    return result.scalar_one_or_none()


async def create_application(
    db: AsyncSession,
    user_id: uuid.UUID,
    job_id: uuid.UUID,
    data: ApplicationCreateRequest,
) -> Application:
    application = Application(
        user_id=user_id,
        job_id=job_id,
        cover_note=data.cover_note,
    )
    db.add(application)
    await db.commit()
    await db.refresh(application)
    return application


async def get_my_applications(
    db: AsyncSession, user_id: uuid.UUID
) -> list[Application]:
    result = await db.execute(
        select(Application)
        .where(Application.user_id == user_id)
        .order_by(Application.created_at.desc())
    )
    return list(result.scalars().all())


async def get_applications_for_job(
    db: AsyncSession, job_id: uuid.UUID
) -> list[Application]:
    # Alle Bewerbungen für eine Stelle — nur für Recruiter sichtbar
    result = await db.execute(
        select(Application)
        .where(Application.job_id == job_id)
        .order_by(Application.created_at.desc())
    )
    return list(result.scalars().all())


async def update_application_status(
    db: AsyncSession,
    application: Application,
    data: ApplicationStatusUpdate,
) -> Application:
    application.status = data.status
    await db.commit()
    await db.refresh(application)
    return application

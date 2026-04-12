import uuid

from sqlalchemy import func, select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.jobs.models import Job
from app.jobs.schemas import JobCreateRequest, JobUpdateRequest


async def create_job(
    db: AsyncSession,
    author_id: uuid.UUID,
    data: JobCreateRequest,
) -> Job:
    job = Job(author_id=author_id, **data.model_dump())
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


async def get_job_by_id(db: AsyncSession, job_id: uuid.UUID) -> Job | None:
    result = await db.execute(select(Job).where(Job.id == job_id))
    return result.scalar_one_or_none()


async def get_jobs(
    db: AsyncSession,
    search: str | None = None,
    company: str | None = None,
    location: str | None = None,
    skill: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[Job], int]:
    query = select(Job).where(Job.is_active == True)

    # der Filter für die Firma (case-insensitive, Teilstring)
    if company:
        query = query.where(Job.company.ilike(f"%{company}%"))

    # der Filter für die Location
    if location:
        query = query.where(Job.location.ilike(f"%{location}%"))

    # der Filter für die Fähigkeiten (PostgreSQL array contains)
    if skill:
        query = query.where(Job.skills_required.any(skill))

    # der Volltextfilter (search_vector @@ plainto_tsquery)
    if search:
        query = query.where(
            Job.search_vector.op("@@")(func.plainto_tsquery("english", search))
        )

    # rechnen die Gesamtzahl der Ergebnisse für die Paginierung
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    # erhalten die Seite
    query = query.order_by(Job.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    items = result.scalars().all()

    return list(items), total


async def get_recommended_jobs(
    db: AsyncSession,
    user_skills: list[str],
    limit: int = 10,
) -> list[Job]:
    """Finden Sie Stellen, bei denen mindestens einer der Fähigkeiten mit dem Profil des Benutzers übereinstimmt."""
    if not user_skills:
        # wenn keine Fähigkeiten vorhanden sind — einfach die letzten Stellen
        result = await db.execute(
            select(Job)
            .where(Job.is_active == True)
            .order_by(Job.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    # bauen die Bedingungen für die Übereinstimmung der Fähigkeiten 
    conditions = [Job.skills_required.any(skill) for skill in user_skills]
    result = await db.execute(
        select(Job)
        .where(Job.is_active == True)
        .where(or_(*conditions))
        .order_by(Job.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())


async def update_job(
    db: AsyncSession,
    job: Job,
    data: JobUpdateRequest,
) -> Job:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(job, field, value)
    await db.commit()
    await db.refresh(job)
    return job


async def delete_job(db: AsyncSession, job: Job) -> None:
    await db.delete(job)
    await db.commit()

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.applications import service
from app.applications.schemas import (
    ApplicationCreateRequest,
    ApplicationResponse,
    ApplicationStatusUpdate,
)
from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.jobs.service import get_job_by_id
from app.users.models import User

router = APIRouter(tags=["Applications"])


@router.post(
    "/jobs/{job_id}/apply",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def apply_for_job(
    job_id: uuid.UUID,
    body: ApplicationCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Stelle prüfen ob sie existiert
    job = await get_job_by_id(db, job_id)
    if not job or not job.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stelle nicht gefunden oder nicht aktiv",
        )

    # Doppelte Bewerbung verhindern
    existing = await service.get_application_by_user_and_job(db, current_user.id, job_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Du hast dich bereits auf diese Stelle beworben",
        )

    return await service.create_application(db, current_user.id, job_id, body)


@router.get("/applications/my", response_model=list[ApplicationResponse])
async def my_applications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await service.get_my_applications(db, current_user.id)


@router.get("/jobs/{job_id}/applications", response_model=list[ApplicationResponse])
async def job_applications(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Nur der Autor der Stelle darf Bewerbungen sehen
    job = await get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stelle nicht gefunden")
    if job.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Kein Zugriff")

    return await service.get_applications_for_job(db, job_id)


@router.patch("/applications/{application_id}/status", response_model=ApplicationResponse)
async def update_status(
    application_id: uuid.UUID,
    body: ApplicationStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    application = await service.get_application_by_id(db, application_id)
    if not application:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bewerbung nicht gefunden")

    # Prüfen ob der aktuelle Benutzer der Autor der Stelle ist
    job = await get_job_by_id(db, application.job_id)
    if not job or job.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Kein Zugriff")

    return await service.update_application_status(db, application, body)

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.core.database import get_db
from app.jobs import service
from app.jobs.schemas import (
    JobCreateRequest,
    JobListResponse,
    JobResponse,
    JobUpdateRequest,
)
from app.profiles.service import get_profile_by_user_id
from app.users.models import User

router = APIRouter(prefix="/jobs", tags=["Jobs"])


def require_recruiter(current_user: User = Depends(get_current_user)) -> User:
    """Prüfen, ob der aktuelle Benutzer ein Recruiter ist."""
    if current_user.role != "recruiter":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only recruiters can manage job postings",
        )
    return current_user


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    body: JobCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_recruiter),
):
    return await service.create_job(db, current_user.id, body)


@router.get("", response_model=JobListResponse)
async def list_jobs(
    search: str | None = Query(None, description="Полнотекстовый поиск"),
    company: str | None = Query(None),
    location: str | None = Query(None),
    skill: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    items, total = await service.get_jobs(
        db,
        search=search,
        company=company,
        location=location,
        skill=skill,
        limit=limit,
        offset=offset,
    )
    return JobListResponse(items=items, total=total)


@router.get("/recommended", response_model=list[JobResponse])
async def recommended_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    profile = await get_profile_by_user_id(db, current_user.id)
    user_skills = profile.skills if profile and profile.skills else []
    return await service.get_recommended_jobs(db, user_skills)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    job = await service.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return job


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: uuid.UUID,
    body: JobUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = await service.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if job.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your job posting")
    return await service.update_job(db, job, body)


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = await service.get_job_by_id(db, job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if job.author_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your job posting")
    await service.delete_job(db, job)

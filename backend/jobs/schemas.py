import uuid
from datetime import datetime

from pydantic import BaseModel


class JobCreateRequest(BaseModel):
    title: str
    description: str | None = None
    company: str | None = None
    location: str | None = None
    skills_required: list[str] | None = None


class JobUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    company: str | None = None
    location: str | None = None
    skills_required: list[str] | None = None
    is_active: bool | None = None


class JobResponse(BaseModel):
    id: uuid.UUID
    author_id: uuid.UUID | None
    title: str
    description: str | None
    company: str | None
    location: str | None
    skills_required: list[str] | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    items: list[JobResponse]
    total: int

import uuid
from datetime import datetime

from pydantic import BaseModel


class ExperienceItem(BaseModel):
    title: str
    company: str
    years: int


class ProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    full_name: str | None
    bio: str | None
    location: str | None
    avatar_url: str | None
    skills: list[str] | None
    experience: list[ExperienceItem] | None
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = None
    bio: str | None = None
    location: str | None = None
    skills: list[str] | None = None
    experience: list[ExperienceItem] | None = None

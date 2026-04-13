import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ApplicationCreateRequest(BaseModel):
    cover_note: str | None = None


class ApplicationStatusUpdate(BaseModel):
    # Nur Recruiter dürfen den Status ändern
    status: Literal["pending", "accepted", "rejected"]


class ApplicationResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    status: str
    cover_note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

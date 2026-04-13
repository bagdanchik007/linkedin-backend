import uuid
from datetime import datetime

from pydantic import BaseModel


class ConnectionResponse(BaseModel):
    id: uuid.UUID
    requester_id: uuid.UUID
    receiver_id: uuid.UUID
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserSuggestionResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str | None = None
    skills: list[str] | None = None

    model_config = {"from_attributes": True}

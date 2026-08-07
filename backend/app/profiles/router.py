from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.auth.dependencies import get_current_user
from app.users.models import User
from app.profiles import service
from app.profiles.schemas import ProfileResponse, ProfileUpdateRequest

router = APIRouter(prefix="/users/me", tags=["Profile"])


@router.get("/profile", response_model=ProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.get_or_create_profile(db, current_user.id)


@router.patch("/profile", response_model=ProfileResponse)
async def update_my_profile(
    body: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await service.update_profile(db, current_user.id, body)

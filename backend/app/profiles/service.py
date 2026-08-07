import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.profiles.models import Profile
from app.profiles.schemas import ProfileUpdateRequest


async def get_profile_by_user_id(db: AsyncSession, user_id: uuid.UUID) -> Profile | None:
    result = await db.execute(select(Profile).where(Profile.user_id == user_id))
    return result.scalar_one_or_none()


async def get_or_create_profile(db: AsyncSession, user_id: uuid.UUID) -> Profile:
    profile = await get_profile_by_user_id(db, user_id)
    if not profile:
        profile = Profile(user_id=user_id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile


async def update_profile(
    db: AsyncSession,
    user_id: uuid.UUID,
    data: ProfileUpdateRequest,
) -> Profile:
    profile = await get_or_create_profile(db, user_id)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "experience" and value is not None:
            # конвертируем Pydantic объекты в dict для JSONB
            value = [item.model_dump() for item in value]
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    return profile

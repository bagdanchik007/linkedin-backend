from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.profiles.router import router as profiles_router

app = FastAPI(
    title="DevConnect API",
    description="LinkedIn-like platform for developers",
    version="0.1.0",
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(profiles_router)


@app.get("/health")
async def health():
    return {"status": "ok"}

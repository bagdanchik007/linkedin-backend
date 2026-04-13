from fastapi import FastAPI

from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.profiles.router import router as profiles_router
from app.jobs.router import router as jobs_router
from app.applications.router import router as applications_router
from app.connections.router import router as connections_router

app = FastAPI(
    title="DevConnect API",
    description="LinkedIn-like platform for developers",
    version="0.1.0",
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(profiles_router)
app.include_router(jobs_router)
app.include_router(applications_router)
app.include_router(connections_router)


@app.get("/health")
async def health():
    return {"status": "ok"}

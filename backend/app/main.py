import os

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.auth.router import router as auth_router
from app.users.router import router as users_router
from app.profiles.router import router as profiles_router
from app.jobs.router import router as jobs_router
from app.applications.router import router as applications_router
from app.connections.router import router as connections_router
from app.notifications.router import router as notifications_router

app = FastAPI(
    title="DevConnect API",
    description="LinkedIn-like Plattform für Entwickler",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(profiles_router)
app.include_router(jobs_router)
app.include_router(applications_router)
app.include_router(connections_router)
app.include_router(notifications_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


# Statische Dateien (Frontend HTML) ausliefern
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/")
    async def frontend():
        """Startseite — HTML Frontend ausliefern."""
        return FileResponse(os.path.join(static_dir, "index.html"))

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

# Separate In-Memory-Datenbank für Tests — kein PostgreSQL nötig
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

session_maker_test = async_sessionmaker(
    engine_test,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    """Testdatenbank statt echter Datenbank verwenden."""
    async with session_maker_test() as session:
        yield session


# FastAPI Dependency überschreiben
app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Tabellen vor jedem Test erstellen und danach löschen."""
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    """HTTP-Testclient für FastAPI."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c


@pytest_asyncio.fixture
async def registered_user(client: AsyncClient) -> dict:
    """Einen registrierten Benutzer erstellen und Tokens zurückgeben."""
    response = await client.post("/auth/register", json={
        "email": "test@devconnect.de",
        "password": "sicherespasswort123",
    })
    return response.json()


@pytest_asyncio.fixture
async def auth_headers(registered_user: dict) -> dict:
    """Autorisierungs-Header mit Access Token."""
    return {"Authorization": f"Bearer {registered_user['access_token']}"}


@pytest_asyncio.fixture
async def second_user(client: AsyncClient) -> dict:
    """Zweiten Benutzer für Tests mit mehreren Nutzern erstellen."""
    response = await client.post("/auth/register", json={
        "email": "zweiter@devconnect.de",
        "password": "sicherespasswort123",
    })
    return response.json()


@pytest_asyncio.fixture
async def second_auth_headers(second_user: dict) -> dict:
    """Autorisierungs-Header für zweiten Benutzer."""
    return {"Authorization": f"Bearer {second_user['access_token']}"}

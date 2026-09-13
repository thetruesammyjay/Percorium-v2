from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import Settings, get_settings
from app.db.models import Base


@lru_cache
def get_engine() -> AsyncEngine:
    settings = get_settings()
    kwargs: dict[str, object] = {"echo": settings.sql_echo, "pool_pre_ping": True}
    if settings.database_url.startswith("sqlite"):
        kwargs["poolclass"] = NullPool
    return create_async_engine(settings.database_url, **kwargs)


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(), expire_on_commit=False, autoflush=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with get_session_factory()() as session:
        yield session


async def check_database() -> None:
    async with get_engine().connect() as connection:
        await connection.execute(text("SELECT 1"))


async def initialize_database(settings: Settings | None = None) -> None:
    active_settings = settings or get_settings()
    if not active_settings.auto_create_db or active_settings.is_production:
        return
    async with get_engine().begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def dispose_engine() -> None:
    if get_engine.cache_info().currsize:
        await get_engine().dispose()
    get_engine.cache_clear()
    get_session_factory.cache_clear()

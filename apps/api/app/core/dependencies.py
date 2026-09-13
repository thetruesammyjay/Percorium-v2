from collections.abc import AsyncIterator

import httpx
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_session


def settings_dependency() -> Settings:
    return get_settings()


async def database_session() -> AsyncIterator[AsyncSession]:
    async for session in get_session():
        yield session


def http_client(request: Request) -> httpx.AsyncClient:
    client = getattr(request.app.state, "http_client", None)
    if client is None:
        raise RuntimeError("HTTP client is not initialized")
    return client

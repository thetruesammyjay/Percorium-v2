import httpx
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.dependencies import database_session, http_client, settings_dependency
from app.schemas.news import NewsResponse
from app.services.news_service import NewsService

router = APIRouter()


@router.get("", response_model=NewsResponse)
async def get_news(
    symbol: str | None = Query(default=None, min_length=1, max_length=12),
    days: int = Query(default=7, ge=1, le=30),
    session: AsyncSession = Depends(database_session),
    settings: Settings = Depends(settings_dependency),
    client: httpx.AsyncClient = Depends(http_client),
) -> NewsResponse:
    return await NewsService(session, settings, client).get(symbol, days=days)

import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.dependencies import database_session, http_client, settings_dependency
from app.schemas.quotes import QuoteRequest, QuoteResponse
from app.services.quote_service import QuoteService

router = APIRouter()


@router.post("", response_model=QuoteResponse)
async def quote(
    request: QuoteRequest,
    session: AsyncSession = Depends(database_session),
    settings: Settings = Depends(settings_dependency),
    client: httpx.AsyncClient = Depends(http_client),
) -> QuoteResponse:
    return await QuoteService(session, settings, client).create_quote(request)

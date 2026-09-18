import httpx
from fastapi import APIRouter, Depends, Query

from app.core.config import Settings
from app.core.dependencies import http_client, settings_dependency
from app.schemas.market import MarketFeedResponse
from app.services.crypto_market_service import CryptoMarketService
from app.services.market_service import MarketService

router = APIRouter()


@router.get("", response_model=MarketFeedResponse)
async def get_market_feed(
    symbols: str | None = Query(default=None, min_length=1, max_length=120),
    settings: Settings = Depends(settings_dependency),
    client: httpx.AsyncClient = Depends(http_client),
) -> MarketFeedResponse:
    return await MarketService(settings, client).get_feed(symbols)


@router.get("/crypto", response_model=MarketFeedResponse)
async def get_crypto_market_feed(
    mints: str | None = Query(default=None, min_length=32, max_length=3000),
    settings: Settings = Depends(settings_dependency),
    client: httpx.AsyncClient = Depends(http_client),
) -> MarketFeedResponse:
    return await CryptoMarketService(settings, client).get_feed(mints)

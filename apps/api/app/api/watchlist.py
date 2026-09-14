import httpx
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.dependencies import database_session, http_client, settings_dependency
from app.core.security import WalletPrincipal, get_wallet_principal
from app.core.validators import require_solana_address
from app.lib.allowlist import AllowlistTab
from app.schemas.watchlist import WatchlistItem, WatchlistResponse
from app.services.watchlist_service import WatchlistService

router = APIRouter()


def service(session: AsyncSession, settings: Settings, client: httpx.AsyncClient) -> WatchlistService:
    return WatchlistService(session, settings, client)


@router.get("", response_model=WatchlistResponse)
async def list_watchlist(
    session: AsyncSession = Depends(database_session),
    settings: Settings = Depends(settings_dependency),
    client: httpx.AsyncClient = Depends(http_client),
    principal: WalletPrincipal = Depends(get_wallet_principal),
) -> WatchlistResponse:
    return await service(session, settings, client).list(principal.wallet)


@router.post("/{mint}", response_model=WatchlistItem, status_code=201)
async def add_watchlist(
    mint: str,
    tab: AllowlistTab = Query(default="stocks"),
    session: AsyncSession = Depends(database_session),
    settings: Settings = Depends(settings_dependency),
    client: httpx.AsyncClient = Depends(http_client),
    principal: WalletPrincipal = Depends(get_wallet_principal),
) -> WatchlistItem:
    require_solana_address(mint, field="mint")
    return await service(session, settings, client).add(principal.wallet, mint, tab)


@router.delete("/{mint}", status_code=204)
async def remove_watchlist(
    mint: str,
    session: AsyncSession = Depends(database_session),
    settings: Settings = Depends(settings_dependency),
    client: httpx.AsyncClient = Depends(http_client),
    principal: WalletPrincipal = Depends(get_wallet_principal),
) -> None:
    require_solana_address(mint, field="mint")
    await service(session, settings, client).remove(principal.wallet, mint)
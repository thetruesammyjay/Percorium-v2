from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import database_session
from app.core.security import WalletPrincipal, get_wallet_principal
from app.core.validators import require_solana_address
from app.schemas.watchlist import WatchlistItem, WatchlistResponse
from app.services.watchlist_service import WatchlistService

router = APIRouter()


@router.get("", response_model=WatchlistResponse)
async def list_watchlist(
    session: AsyncSession = Depends(database_session),
    principal: WalletPrincipal = Depends(get_wallet_principal),
) -> WatchlistResponse:
    return await WatchlistService(session).list(principal.wallet)


@router.post("/{mint}", response_model=WatchlistItem, status_code=201)
async def add_watchlist(
    mint: str,
    session: AsyncSession = Depends(database_session),
    principal: WalletPrincipal = Depends(get_wallet_principal),
) -> WatchlistItem:
    require_solana_address(mint, field="mint")
    return await WatchlistService(session).add(principal.wallet, mint)


@router.delete("/{mint}", status_code=204)
async def remove_watchlist(
    mint: str,
    session: AsyncSession = Depends(database_session),
    principal: WalletPrincipal = Depends(get_wallet_principal),
) -> None:
    require_solana_address(mint, field="mint")
    await WatchlistService(session).remove(principal.wallet, mint)

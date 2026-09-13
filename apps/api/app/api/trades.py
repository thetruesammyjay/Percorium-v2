import httpx
from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.dependencies import database_session, http_client, settings_dependency
from app.core.exceptions import AppError
from app.core.security import WalletPrincipal, get_wallet_principal
from app.schemas.trades import TradeCreate, TradeListResponse, TradeResponse, TradeSubmit
from app.services.trade_service import TradeService

router = APIRouter()


@router.get("", response_model=TradeListResponse)
async def list_trades(
    limit: int = Query(default=50, ge=1, le=100),
    session: AsyncSession = Depends(database_session),
    settings: Settings = Depends(settings_dependency),
    client: httpx.AsyncClient = Depends(http_client),
    principal: WalletPrincipal = Depends(get_wallet_principal),
) -> TradeListResponse:
    return await TradeService(session, settings, client).list_trades(principal.wallet, limit=limit)


@router.post("", response_model=TradeResponse)
async def create_trade(
    request: TradeCreate,
    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=8, max_length=255),
    session: AsyncSession = Depends(database_session),
    settings: Settings = Depends(settings_dependency),
    client: httpx.AsyncClient = Depends(http_client),
    principal: WalletPrincipal = Depends(get_wallet_principal),
) -> TradeResponse:
    if request.wallet != principal.wallet:
        raise AppError(
            "The trade wallet does not match the authenticated wallet.", code="wallet_mismatch", status_code=403
        )
    return await TradeService(session, settings, client).create_trade(request, idempotency_key)


@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(
    trade_id: str,
    session: AsyncSession = Depends(database_session),
    settings: Settings = Depends(settings_dependency),
    client: httpx.AsyncClient = Depends(http_client),
    principal: WalletPrincipal = Depends(get_wallet_principal),
) -> TradeResponse:
    return await TradeService(session, settings, client).get_trade(trade_id, principal.wallet)


@router.post("/{trade_id}/submit", response_model=TradeResponse)
async def submit_trade(
    trade_id: str,
    request: TradeSubmit,
    session: AsyncSession = Depends(database_session),
    settings: Settings = Depends(settings_dependency),
    client: httpx.AsyncClient = Depends(http_client),
    principal: WalletPrincipal = Depends(get_wallet_principal),
) -> TradeResponse:
    if request.wallet != principal.wallet:
        raise AppError(
            "The submitted wallet does not match the authenticated wallet.", code="wallet_mismatch", status_code=403
        )
    return await TradeService(session, settings, client).submit_trade(trade_id, request.wallet, request.signature)

import httpx
from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.dependencies import database_session, http_client, settings_dependency
from app.core.exceptions import AppError
from app.core.security import WalletPrincipal, get_wallet_principal
from app.schemas.orders import OrderCreate, OrderListResponse, OrderResponse, OrderSubmit
from app.services.order_service import OrderService

router = APIRouter()


@router.get("", response_model=OrderListResponse)
async def list_orders(
    limit: int = Query(default=50, ge=1, le=100),
    session: AsyncSession = Depends(database_session),
    settings: Settings = Depends(settings_dependency),
    client: httpx.AsyncClient = Depends(http_client),
    principal: WalletPrincipal = Depends(get_wallet_principal),
) -> OrderListResponse:
    return await OrderService(session, settings, client).list_orders(principal.wallet, limit=limit)


@router.post("", response_model=OrderResponse)
async def create_order(
    request: OrderCreate,
    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=8, max_length=255),
    session: AsyncSession = Depends(database_session),
    settings: Settings = Depends(settings_dependency),
    client: httpx.AsyncClient = Depends(http_client),
    principal: WalletPrincipal = Depends(get_wallet_principal),
) -> OrderResponse:
    if request.wallet != principal.wallet:
        raise AppError(
            "The order wallet does not match the authenticated wallet.", code="wallet_mismatch", status_code=403
        )
    return await OrderService(session, settings, client).create_order(request, idempotency_key)


@router.post("/{order_id}/submit", response_model=OrderResponse)
async def submit_order(
    order_id: str,
    request: OrderSubmit,
    session: AsyncSession = Depends(database_session),
    settings: Settings = Depends(settings_dependency),
    client: httpx.AsyncClient = Depends(http_client),
    principal: WalletPrincipal = Depends(get_wallet_principal),
) -> OrderResponse:
    if request.wallet != principal.wallet:
        raise AppError(
            "The submitted wallet does not match the authenticated wallet.", code="wallet_mismatch", status_code=403
        )
    return await OrderService(session, settings, client).submit_order(order_id, request.wallet, request.signature)

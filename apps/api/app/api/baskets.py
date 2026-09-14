import httpx
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.dependencies import database_session, http_client, settings_dependency
from app.core.security import WalletPrincipal, get_wallet_principal
from app.schemas.baskets import BasketCreate, BasketListResponse, BasketResponse
from app.services.basket_service import BasketService

router = APIRouter()


def service(session: AsyncSession, settings: Settings, client: httpx.AsyncClient) -> BasketService:
    return BasketService(session, settings, client)


@router.get("", response_model=BasketListResponse)
async def list_baskets(
    limit: int = Query(default=50, ge=1, le=100),
    session: AsyncSession = Depends(database_session),
    settings: Settings = Depends(settings_dependency),
    client: httpx.AsyncClient = Depends(http_client),
) -> BasketListResponse:
    return await service(session, settings, client).list_public(limit=limit)


@router.get("/{slug}", response_model=BasketResponse)
async def get_basket(
    slug: str,
    session: AsyncSession = Depends(database_session),
    settings: Settings = Depends(settings_dependency),
    client: httpx.AsyncClient = Depends(http_client),
) -> BasketResponse:
    return await service(session, settings, client).get_public(slug)


@router.post("", response_model=BasketResponse, status_code=201)
async def create_basket(
    request: BasketCreate,
    session: AsyncSession = Depends(database_session),
    settings: Settings = Depends(settings_dependency),
    client: httpx.AsyncClient = Depends(http_client),
    principal: WalletPrincipal = Depends(get_wallet_principal),
) -> BasketResponse:
    return await service(session, settings, client).create(request, principal.wallet)
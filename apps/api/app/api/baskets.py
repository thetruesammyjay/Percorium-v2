from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import database_session
from app.core.security import WalletPrincipal, get_wallet_principal
from app.schemas.baskets import BasketCreate, BasketListResponse, BasketResponse
from app.services.basket_service import BasketService

router = APIRouter()


@router.get("", response_model=BasketListResponse)
async def list_baskets(
    limit: int = Query(default=50, ge=1, le=100),
    session: AsyncSession = Depends(database_session),
) -> BasketListResponse:
    return await BasketService(session).list_public(limit=limit)


@router.get("/{slug}", response_model=BasketResponse)
async def get_basket(
    slug: str,
    session: AsyncSession = Depends(database_session),
) -> BasketResponse:
    return await BasketService(session).get_public(slug)


@router.post("", response_model=BasketResponse, status_code=201)
async def create_basket(
    request: BasketCreate,
    session: AsyncSession = Depends(database_session),
    principal: WalletPrincipal = Depends(get_wallet_principal),
) -> BasketResponse:
    return await BasketService(session).create(request, principal.wallet)

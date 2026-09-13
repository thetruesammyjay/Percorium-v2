import httpx
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.dependencies import database_session, http_client, settings_dependency
from app.core.security import WalletPrincipal, get_wallet_principal
from app.schemas.portfolio import PortfolioResponse
from app.services.portfolio_service import PortfolioService

router = APIRouter()


@router.get("", response_model=PortfolioResponse)
async def get_portfolio(
    session: AsyncSession = Depends(database_session),
    settings: Settings = Depends(settings_dependency),
    client: httpx.AsyncClient = Depends(http_client),
    principal: WalletPrincipal = Depends(get_wallet_principal),
) -> PortfolioResponse:
    return await PortfolioService(session, settings, client).get(principal.wallet)

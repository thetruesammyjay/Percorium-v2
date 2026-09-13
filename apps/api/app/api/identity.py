from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import database_session
from app.core.security import WalletPrincipal, get_wallet_principal
from app.schemas.identity import IdentityResponse, IdentityUpdate
from app.services.identity_service import IdentityService

router = APIRouter()


@router.get("/me", response_model=IdentityResponse)
async def get_identity(
    session: AsyncSession = Depends(database_session),
    principal: WalletPrincipal = Depends(get_wallet_principal),
) -> IdentityResponse:
    return await IdentityService(session).get_or_create(principal.wallet)


@router.patch("/me", response_model=IdentityResponse)
async def update_identity(
    request: IdentityUpdate,
    session: AsyncSession = Depends(database_session),
    principal: WalletPrincipal = Depends(get_wallet_principal),
) -> IdentityResponse:
    return await IdentityService(session).update(principal.wallet, request)

from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import database_session
from app.core.exceptions import AppError
from app.core.security import WalletPrincipal, get_wallet_principal
from app.schemas.gifts import GiftCreate, GiftResponse
from app.services.gift_service import GiftService

router = APIRouter()


@router.post("", response_model=GiftResponse, status_code=201)
async def create_gift(
    request: GiftCreate,
    idempotency_key: str = Header(..., alias="Idempotency-Key", min_length=8, max_length=255),
    session: AsyncSession = Depends(database_session),
    principal: WalletPrincipal = Depends(get_wallet_principal),
) -> GiftResponse:
    if request.sender_wallet != principal.wallet:
        raise AppError(
            "The sender wallet does not match the authenticated wallet.", code="wallet_mismatch", status_code=403
        )
    return await GiftService(session).create(request, idempotency_key)


@router.get("/{claim_id}", response_model=GiftResponse)
async def get_gift(claim_id: str, session: AsyncSession = Depends(database_session)) -> GiftResponse:
    return await GiftService(session).get(claim_id)

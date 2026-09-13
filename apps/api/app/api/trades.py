from fastapi import APIRouter

from app.schemas.trades import TradeCreate, TradeResponse
from app.services.trade_service import create_trade_intent

router = APIRouter()


@router.post("", response_model=TradeResponse)
async def create_trade(request: TradeCreate) -> TradeResponse:
    return await create_trade_intent(request)

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import RailName


class TradeCreate(BaseModel):
    rail: RailName = "solana"
    input_mint: str
    output_mint: str
    amount: Decimal = Field(gt=0)
    wallet: str
    slippage_bps: int = Field(default=100, ge=1, le=5000)
    order_type: Literal["market", "limit", "dca"] = "market"


class TradeResponse(BaseModel):
    status: Literal["awaiting_signature", "not_configured"]
    rail: RailName
    fee_bps: int
    wallet: str
    message: str

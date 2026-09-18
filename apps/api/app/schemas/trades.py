from datetime import datetime
from typing import Literal

from pydantic import Field

from app.schemas.common import APIModel, AtomicAmount, RailName, TradeStatus


class TradeCreate(APIModel):
    rail: RailName = RailName.SOLANA
    tab: Literal["stocks", "pre-ipo", "new"] = "stocks"
    sell_mint: str = Field(min_length=1, max_length=64)
    buy_mint: str = Field(min_length=1, max_length=64)
    sell_amount: AtomicAmount
    wallet: str = Field(min_length=32, max_length=64)
    slippage_bps: int = Field(default=100, ge=1, le=5_000)
    order_type: Literal["market"] = "market"
    copy_master: bool = False
    is_private: bool = False


class TradeSubmit(APIModel):
    wallet: str = Field(min_length=32, max_length=64)
    signature: str = Field(min_length=32, max_length=128)


class TradeResponse(APIModel):
    id: str | None = None
    status: TradeStatus | Literal["not_configured"]
    rail: RailName
    tab: Literal["stocks", "pre-ipo", "new"] = "stocks"
    wallet: str
    sell_mint: str
    buy_mint: str
    sell_amount: AtomicAmount
    expected_buy_amount: AtomicAmount | None = None
    price_impact_bps: int | None = None
    fee_bps: int
    platform_fee: AtomicAmount
    copy_master_fee: AtomicAmount = "0"
    percorium_fee: AtomicAmount = "0"
    network_fee: str = "estimated"
    total_debit: AtomicAmount
    expires_at: datetime | None = None
    transaction: str | None = None
    tx_signature: str | None = None
    signing_required: bool = True
    message: str

class TradeListResponse(APIModel):
    items: list[TradeResponse]

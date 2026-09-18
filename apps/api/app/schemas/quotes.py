from datetime import datetime
from typing import Any, Literal

from pydantic import AliasChoices, Field

from app.schemas.common import APIModel, AtomicAmount, RailName


class QuoteRequest(APIModel):
    rail: RailName = RailName.SOLANA
    tab: Literal["stocks", "pre-ipo", "new"] = "stocks"
    sell_mint: str = Field(validation_alias=AliasChoices("sell_mint", "input_mint"), min_length=1, max_length=64)
    buy_mint: str = Field(validation_alias=AliasChoices("buy_mint", "output_mint"), min_length=1, max_length=64)
    sell_amount: AtomicAmount
    slippage_bps: int = Field(default=100, ge=1, le=5_000)
    mode: Literal["exact_in", "exact_out"] = "exact_in"


class QuoteResponse(APIModel):
    status: Literal["ready", "not_configured"]
    rail: RailName
    tab: Literal["stocks", "pre-ipo", "new"] = "stocks"
    sell_mint: str
    buy_mint: str
    sell_amount: AtomicAmount
    expected_buy_amount: AtomicAmount | None = None
    price_impact_bps: int | None = None
    fee_bps: int
    platform_fee: AtomicAmount
    network_fee: str = "estimated"
    total_debit: AtomicAmount
    expires_at: datetime | None = None
    transaction: str | None = None
    signing_required: bool = True
    message: str | None = None
    provider_quote: dict[str, Any] | None = Field(default=None, exclude=True)
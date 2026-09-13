from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.common import RailName


class QuoteRequest(BaseModel):
    rail: RailName = "solana"
    input_mint: str
    output_mint: str
    amount: Decimal = Field(gt=0)
    input_decimals: int = Field(default=6, ge=0, le=18)
    mode: Literal["exact_in", "exact_out"] = "exact_in"


class QuoteResponse(BaseModel):
    status: Literal["ready", "not_configured"]
    rail: RailName
    input_mint: str
    output_mint: str
    amount: Decimal
    fee_bps: int
    fee_amount: Decimal | None = None
    message: str | None = None

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Literal

from pydantic import Field, model_validator

from app.schemas.common import APIModel, AtomicAmount, OrderStatus, RailName


class OrderCreate(APIModel):
    rail: RailName = RailName.SOLANA
    tab: Literal["stocks", "pre-ipo"] = "stocks"
    wallet: str = Field(min_length=32, max_length=64)
    input_mint: str = Field(min_length=1, max_length=64)
    output_mint: str = Field(min_length=1, max_length=64)
    amount: AtomicAmount
    order_type: Literal["limit", "dca"]
    limit_price: str | None = Field(default=None, min_length=1, max_length=64)
    interval_seconds: int | None = Field(default=None, ge=60, le=31_536_000)
    occurrences: int | None = Field(default=None, ge=1, le=10_000)
    slippage_bps: int = Field(default=100, ge=1, le=5_000)

    @model_validator(mode="after")
    def validate_order_parameters(self) -> "OrderCreate":
        if self.input_mint == self.output_mint:
            raise ValueError("input_mint and output_mint must be different")
        if self.order_type == "limit" and self.limit_price is None:
            raise ValueError("limit_price is required for limit orders")
        if self.order_type == "dca" and (self.interval_seconds is None or self.occurrences is None):
            raise ValueError("interval_seconds and occurrences are required for DCA orders")
        if self.limit_price is not None:
            try:
                price = Decimal(self.limit_price)
            except InvalidOperation as exc:
                raise ValueError("limit_price must be a positive decimal string") from exc
            if not price.is_finite() or price <= 0:
                raise ValueError("limit_price must be a positive decimal string")
        return self


class OrderSubmit(APIModel):
    wallet: str = Field(min_length=32, max_length=64)
    signature: str = Field(min_length=32, max_length=128)


class OrderResponse(APIModel):
    id: str | None = None
    status: OrderStatus | Literal["not_configured"]
    rail: RailName
    tab: Literal["stocks", "pre-ipo"] = "stocks"
    wallet: str
    order_type: Literal["limit", "dca"]
    input_mint: str
    output_mint: str
    amount: AtomicAmount
    limit_price: str | None = None
    interval_seconds: int | None = None
    occurrences: int | None = None
    fee_bps: int
    platform_fee: AtomicAmount
    total_debit: AtomicAmount
    expires_at: datetime | None = None
    transaction: str | None = None
    provider_order_id: str | None = None
    tx_signature: str | None = None
    signing_required: bool = True
    message: str


class OrderListResponse(APIModel):
    items: list[OrderResponse]
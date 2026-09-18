from datetime import datetime

from pydantic import Field

from app.schemas.common import APIModel


class MarketQuote(APIModel):
    symbol: str = Field(min_length=1, max_length=12)
    mint: str | None = None
    logo_url: str | None = Field(default=None, max_length=500)
    price: float = Field(ge=0)
    change: float
    change_percent: float
    high: float | None = Field(default=None, ge=0)
    low: float | None = Field(default=None, ge=0)
    open: float | None = Field(default=None, ge=0)
    previous_close: float | None = Field(default=None, ge=0)
    as_of: datetime | None = None
    source: str = "finnhub"


class MarketFeedResponse(APIModel):
    items: list[MarketQuote]
    symbols: list[str]
    configured: bool
    source: str = "finnhub"
    fetched_at: datetime
    message: str | None = None

from typing import Literal

from app.schemas.common import APIModel, AtomicAmount


class PortfolioToken(APIModel):
    mint: str
    symbol: str
    name: str
    raw_amount: AtomicAmount
    decimals: int
    value_usd: str | None = None


class PortfolioResponse(APIModel):
    status: Literal["ready", "not_configured"]
    wallet: str
    native_balance_lamports: str
    tokens: list[PortfolioToken]
    source: str = "alchemy"
    message: str | None = None

from datetime import datetime

from pydantic import Field

from app.schemas.common import APIModel, AssetKind, Pagination, SolanaAddress


class Asset(APIModel):
    mint: SolanaAddress
    symbol: str = Field(min_length=1, max_length=24)
    name: str = Field(min_length=1, max_length=160)
    kind: AssetKind
    decimals: int = Field(default=6, ge=0, le=18)
    featured: bool = False
    news_symbol: str | None = Field(default=None, max_length=12)
    logo_url: str | None = Field(default=None, max_length=500)
    verified: bool = True
    tradable: bool = True
    updated_at: datetime | None = None


class AssetListResponse(Pagination):
    items: list[Asset]
    source: str = "jupiter"
    configured: bool = False
    message: str | None = None

from datetime import datetime

from pydantic import Field

from app.schemas.common import APIModel, AssetKind, Pagination, SolanaAddress


class Asset(APIModel):
    mint: SolanaAddress
    symbol: str = Field(min_length=1, max_length=24)
    name: str = Field(min_length=1, max_length=160)
    kind: AssetKind
    logo_url: str | None = Field(default=None, max_length=500)
    verified: bool = True
    tradable: bool = True
    updated_at: datetime | None = None


class AssetListResponse(Pagination):
    items: list[Asset]
    source: str = "sunrise"
    configured: bool = False
    message: str | None = None

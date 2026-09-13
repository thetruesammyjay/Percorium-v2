from pydantic import BaseModel

from app.schemas.common import AssetKind


class Asset(BaseModel):
    symbol: str
    name: str
    mint: str
    kind: AssetKind
    logo_url: str | None = None


class AssetListResponse(BaseModel):
    items: list[Asset]
    source: str = "sunrise"
    configured: bool = False

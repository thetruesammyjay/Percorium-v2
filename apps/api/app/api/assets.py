import httpx
from fastapi import APIRouter, Depends, Query

from app.core.config import Settings
from app.core.dependencies import http_client, settings_dependency
from app.core.exceptions import NotFoundError
from app.core.validators import require_solana_address
from app.lib.allowlist import AllowlistTab
from app.schemas.assets import Asset, AssetListResponse
from app.services.asset_service import AssetService

router = APIRouter()


@router.get("", response_model=AssetListResponse)
async def get_assets(
    query: str | None = Query(default=None, min_length=1, max_length=80),
    tab: AllowlistTab = Query(default="stocks"),
    limit: int = Query(default=50, ge=1, le=100),
    cursor: str | None = Query(default=None, min_length=1, max_length=64),
    settings: Settings = Depends(settings_dependency),
    client: httpx.AsyncClient = Depends(http_client),
) -> AssetListResponse:
    return await AssetService(settings, client).list_official_assets(
        query=query,
        limit=limit,
        cursor=cursor,
        tab=tab,
    )


@router.get("/{mint}", response_model=Asset)
async def get_asset(
    mint: str,
    tab: AllowlistTab | None = Query(default=None),
    settings: Settings = Depends(settings_dependency),
    client: httpx.AsyncClient = Depends(http_client),
) -> Asset:
    require_solana_address(mint, field="mint")
    asset = await AssetService(settings, client).get_official_asset(mint, tab)
    if asset is None:
        raise NotFoundError("official asset")
    return asset
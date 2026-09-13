import httpx
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.dependencies import database_session, http_client, settings_dependency
from app.core.exceptions import NotFoundError
from app.core.validators import require_solana_address
from app.schemas.assets import Asset, AssetListResponse
from app.services.asset_service import AssetService

router = APIRouter()


@router.get("", response_model=AssetListResponse)
async def get_assets(
    query: str | None = Query(default=None, min_length=1, max_length=80),
    limit: int = Query(default=50, ge=1, le=100),
    cursor: str | None = Query(default=None, min_length=1, max_length=64),
    session: AsyncSession = Depends(database_session),
    settings: Settings = Depends(settings_dependency),
    client: httpx.AsyncClient = Depends(http_client),
) -> AssetListResponse:
    return await AssetService(session, settings, client).list_official_assets(query=query, limit=limit, cursor=cursor)


@router.get("/{mint}", response_model=Asset)
async def get_asset(
    mint: str,
    session: AsyncSession = Depends(database_session),
    settings: Settings = Depends(settings_dependency),
    client: httpx.AsyncClient = Depends(http_client),
) -> Asset:
    require_solana_address(mint, field="mint")
    asset = await AssetService(session, settings, client).get_official_asset(mint)
    if asset is None or not asset.verified or not asset.tradable:
        raise NotFoundError("official asset")
    return Asset.model_validate(asset)

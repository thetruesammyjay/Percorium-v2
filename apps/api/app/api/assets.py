from fastapi import APIRouter

from app.schemas.assets import AssetListResponse
from app.services.asset_service import list_official_assets

router = APIRouter()


@router.get("", response_model=AssetListResponse)
async def get_assets(query: str | None = None) -> AssetListResponse:
    """Return the cached Sunrise allowlist once the asset sync is configured."""
    return await list_official_assets(query=query)

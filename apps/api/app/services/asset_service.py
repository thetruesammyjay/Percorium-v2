from app.core.config import get_settings
from app.schemas.assets import AssetListResponse


async def list_official_assets(query: str | None = None) -> AssetListResponse:
    settings = get_settings()
    message = "Sunrise asset sync is not configured."
    if query:
        message = f"Sunrise asset sync is not configured; search deferred for {query!r}."
    return AssetListResponse(
        items=[], source="sunrise", configured=bool(settings.sunrise_api_url), message=message
    )  # type: ignore[call-arg]

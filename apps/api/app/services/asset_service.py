from app.core.config import Settings
from app.lib.allowlist import AllowlistTab, AssetAllowlist
from app.schemas.assets import Asset, AssetListResponse


class AssetService:
    def __init__(self, settings: Settings, client) -> None:
        self.settings = settings
        self.allowlist = AssetAllowlist(settings, client)

    async def list_official_assets(
        self,
        *,
        query: str | None = None,
        limit: int = 50,
        cursor: str | None = None,
        tab: AllowlistTab = "stocks",
    ) -> AssetListResponse:
        assets = await self.allowlist.load(tab)
        normalized_query = (query or "").strip().casefold()
        if normalized_query:
            assets = [
                asset
                for asset in assets
                if normalized_query in asset.symbol.casefold() or normalized_query in asset.name.casefold()
            ]

        start = 0
        if cursor:
            for index, asset in enumerate(assets):
                if asset.mint == cursor:
                    start = index + 1
                    break
        items = assets[start : start + limit]
        next_cursor = assets[start + limit].mint if len(assets) > start + limit else None
        configured = self.allowlist.stocks_configured if tab == "stocks" else self.allowlist.preipo_configured
        source = "sunrise" if tab == "stocks" else "prestocks"
        message = None
        if not configured:
            message = "This discovery source is not configured."
        elif not assets:
            message = "No assets were returned by this discovery source."
        return AssetListResponse(
            items=items,
            source=source,
            configured=configured,
            next_cursor=next_cursor,
            limit=limit,
            message=message,
        )

    async def get_official_asset(self, mint: str, tab: AllowlistTab | None = None) -> Asset | None:
        tabs: tuple[AllowlistTab, ...] = (tab,) if tab is not None else ("stocks", "pre-ipo")
        for current_tab in tabs:
            for asset in await self.allowlist.load(current_tab):
                if asset.mint == mint:
                    return asset
        return None
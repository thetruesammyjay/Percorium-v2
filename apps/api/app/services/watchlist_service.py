from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.validators import require_solana_address
from app.db.repositories import WatchlistRepository
from app.lib.allowlist import AllowlistTab, AssetAllowlist
from app.schemas.watchlist import WatchlistItem, WatchlistResponse


class WatchlistService:
    def __init__(self, session: AsyncSession, settings: Settings, client) -> None:
        self.session = session
        self.watchlist = WatchlistRepository(session)
        self.allowlist = AssetAllowlist(settings, client)

    async def list(self, wallet: str) -> WatchlistResponse:
        require_solana_address(wallet, field="wallet")
        records = await self.watchlist.list_for_wallet(wallet)
        return WatchlistResponse(items=[WatchlistItem.model_validate(record) for record in records])

    async def add(self, wallet: str, mint: str, tab: AllowlistTab = "stocks") -> WatchlistItem:
        require_solana_address(wallet, field="wallet")
        await self.allowlist.assert_asset_allowed(mint, tab)
        record = await self.watchlist.get(wallet, mint)
        if record is None:
            record = await self.watchlist.add(wallet, mint)
            await self.session.commit()
        return WatchlistItem.model_validate(record)

    async def remove(self, wallet: str, mint: str) -> None:
        require_solana_address(wallet, field="wallet")
        require_solana_address(mint, field="mint")
        await self.watchlist.remove(wallet, mint)
        await self.session.commit()
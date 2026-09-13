from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnsupportedAssetError
from app.core.validators import require_solana_address
from app.db.repositories import AssetRepository, WatchlistRepository
from app.schemas.watchlist import WatchlistItem, WatchlistResponse


class WatchlistService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.assets = AssetRepository(session)
        self.watchlist = WatchlistRepository(session)

    async def list(self, wallet: str) -> WatchlistResponse:
        require_solana_address(wallet, field="wallet")
        records = await self.watchlist.list_for_wallet(wallet)
        return WatchlistResponse(items=[WatchlistItem.model_validate(record) for record in records])

    async def add(self, wallet: str, mint: str) -> WatchlistItem:
        require_solana_address(wallet, field="wallet")
        require_solana_address(mint, field="mint")
        asset = await self.assets.get_by_mint(mint)
        if asset is None or not asset.verified or not asset.tradable:
            raise UnsupportedAssetError(mint)
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

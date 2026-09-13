import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.db.models import AssetRecord
from app.db.repositories import AssetRepository
from app.integrations.sunrise import SunriseClient
from app.schemas.assets import Asset, AssetListResponse


class AssetService:
    def __init__(self, session: AsyncSession, settings: Settings, client: httpx.AsyncClient) -> None:
        self.session = session
        self.repository = AssetRepository(session)
        self.settings = settings
        self.sunrise = SunriseClient(settings, client)

    async def list_official_assets(
        self, *, query: str | None = None, limit: int = 50, cursor: str | None = None
    ) -> AssetListResponse:
        records = await self.repository.list_assets(query=query, limit=limit, cursor=cursor)
        configured = self.sunrise.configured
        if not records and configured:
            upstream_assets = await self.sunrise.list_assets(query=query)
            await self.repository.upsert_many([asset.model_dump() for asset in upstream_assets])
            await self.session.commit()
            records = await self.repository.list_assets(query=query, limit=limit, cursor=cursor)
        items = [self._to_schema(record) for record in records[:limit]]
        next_cursor = records[limit].mint if len(records) > limit else None
        return AssetListResponse(
            items=items,
            source="sunrise",
            configured=configured,
            next_cursor=next_cursor,
            limit=limit,
            message=None if configured else "Sunrise asset sync is not configured.",
        )

    async def get_official_asset(self, mint: str) -> AssetRecord | None:
        return await self.repository.get_by_mint(mint)

    @staticmethod
    def _to_schema(record: AssetRecord) -> Asset:
        return Asset.model_validate(record)

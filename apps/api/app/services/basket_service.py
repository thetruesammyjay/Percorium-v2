import json
import re
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.exceptions import AppError, NotFoundError
from app.core.validators import require_solana_address
from app.db.models import BasketRecord
from app.lib.allowlist import AssetAllowlist
from app.schemas.baskets import BasketCreate, BasketItem, BasketListResponse, BasketResponse


class BasketService:
    def __init__(self, session: AsyncSession, settings: Settings, client) -> None:
        self.session = session
        self.allowlist = AssetAllowlist(settings, client)

    async def create(self, request: BasketCreate, owner_wallet: str | None) -> BasketResponse:
        for item in request.items:
            require_solana_address(item.mint, field="mint")
            await self.allowlist.assert_asset_allowed(item.mint, request.tab)
        slug = request.slug or self._slug(request.name)
        existing = await self.session.scalar(select(BasketRecord).where(BasketRecord.slug == slug))
        if existing is not None:
            raise AppError("That basket slug is already in use.", code="basket_slug_taken", status_code=409)
        record = BasketRecord(
            owner_wallet=owner_wallet,
            slug=slug,
            name=request.name,
            items_json=json.dumps([item.model_dump() for item in request.items], separators=(",", ":")),
            is_public=request.is_public,
        )
        self.session.add(record)
        await self.session.commit()
        return self._to_response(record)

    async def list_public(self, limit: int = 50) -> BasketListResponse:
        result = await self.session.execute(
            select(BasketRecord)
            .where(BasketRecord.is_public.is_(True))
            .order_by(BasketRecord.created_at.desc())
            .limit(limit)
        )
        return BasketListResponse(items=[self._to_response(record) for record in result.scalars().all()])

    async def get_public(self, slug: str) -> BasketResponse:
        record = await self.session.scalar(
            select(BasketRecord).where(BasketRecord.slug == slug, BasketRecord.is_public.is_(True))
        )
        if record is None:
            raise NotFoundError("basket")
        return self._to_response(record)

    @staticmethod
    def _slug(name: str) -> str:
        normalized = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "basket"
        return f"{normalized[:60]}-{uuid4().hex[:8]}"

    @staticmethod
    def _to_response(record: BasketRecord) -> BasketResponse:
        return BasketResponse(
            id=record.id,
            slug=record.slug,
            name=record.name,
            items=[BasketItem.model_validate(item) for item in json.loads(record.items_json)],
            is_public=record.is_public,
            created_at=record.created_at or datetime.now(timezone.utc),
        )
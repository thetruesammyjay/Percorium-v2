from collections.abc import Sequence

from sqlalchemy import delete, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    AssetRecord,
    IdentityRecord,
    NewsCacheRecord,
    OrderIntentRecord,
    TradeIntentRecord,
    WatchlistRecord,
)


class AssetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_assets(
        self, *, query: str | None = None, limit: int = 50, cursor: str | None = None
    ) -> Sequence[AssetRecord]:
        statement = select(AssetRecord).where(AssetRecord.verified.is_(True), AssetRecord.tradable.is_(True))
        if query:
            search = f"%{query.strip()}%"
            statement = statement.where(or_(AssetRecord.symbol.ilike(search), AssetRecord.name.ilike(search)))
        if cursor:
            statement = statement.where(AssetRecord.mint > cursor)
        statement = statement.order_by(AssetRecord.mint).limit(limit + 1)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_by_mint(self, mint: str) -> AssetRecord | None:
        result = await self.session.execute(select(AssetRecord).where(AssetRecord.mint == mint))
        return result.scalar_one_or_none()

    async def upsert_many(self, assets: list[dict[str, object]]) -> None:
        for payload in assets:
            mint = str(payload["mint"])
            existing = await self.get_by_mint(mint)
            if existing is None:
                self.session.add(AssetRecord(**payload))
            else:
                for key, value in payload.items():
                    setattr(existing, key, value)
        await self.session.flush()


class TradeIntentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, record_id: str) -> TradeIntentRecord | None:
        return await self.session.get(TradeIntentRecord, record_id)

    async def get_by_idempotency(self, wallet: str, idempotency_key: str) -> TradeIntentRecord | None:
        result = await self.session.execute(
            select(TradeIntentRecord).where(
                TradeIntentRecord.wallet == wallet,
                TradeIntentRecord.idempotency_key == idempotency_key,
            )
        )
        return result.scalar_one_or_none()

    async def get_for_wallet(self, wallet: str, limit: int = 50) -> Sequence[TradeIntentRecord]:
        result = await self.session.execute(
            select(TradeIntentRecord)
            .where(TradeIntentRecord.wallet == wallet)
            .order_by(TradeIntentRecord.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def create(self, **payload: object) -> TradeIntentRecord:
        record = TradeIntentRecord(**payload)
        self.session.add(record)
        await self.session.flush()
        return record

    async def set_submitted(self, record: TradeIntentRecord, signature: str) -> TradeIntentRecord:
        record.tx_signature = signature
        record.status = "submitted"
        await self.session.flush()
        return record


class OrderIntentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, record_id: str) -> OrderIntentRecord | None:
        return await self.session.get(OrderIntentRecord, record_id)

    async def get_by_idempotency(self, wallet: str, idempotency_key: str) -> OrderIntentRecord | None:
        result = await self.session.execute(
            select(OrderIntentRecord).where(
                OrderIntentRecord.wallet == wallet,
                OrderIntentRecord.idempotency_key == idempotency_key,
            )
        )
        return result.scalar_one_or_none()

    async def get_for_wallet(self, wallet: str, limit: int = 50) -> Sequence[OrderIntentRecord]:
        result = await self.session.execute(
            select(OrderIntentRecord)
            .where(OrderIntentRecord.wallet == wallet)
            .order_by(OrderIntentRecord.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

    async def create(self, **payload: object) -> OrderIntentRecord:
        record = OrderIntentRecord(**payload)
        self.session.add(record)
        await self.session.flush()
        return record

    async def set_submitted(self, record: OrderIntentRecord, signature: str) -> OrderIntentRecord:
        record.tx_signature = signature
        record.status = "submitted"
        await self.session.flush()
        return record


class IdentityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, wallet: str) -> IdentityRecord | None:
        return await self.session.get(IdentityRecord, wallet)

    async def get_by_handle(self, handle: str) -> IdentityRecord | None:
        result = await self.session.execute(select(IdentityRecord).where(IdentityRecord.handle == handle))
        return result.scalar_one_or_none()

    async def create(self, wallet: str, handle: str) -> IdentityRecord:
        record = IdentityRecord(wallet=wallet, handle=handle)
        self.session.add(record)
        await self.session.flush()
        return record


class WatchlistRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_for_wallet(self, wallet: str) -> Sequence[WatchlistRecord]:
        result = await self.session.execute(
            select(WatchlistRecord).where(WatchlistRecord.wallet == wallet).order_by(WatchlistRecord.created_at.desc())
        )
        return result.scalars().all()

    async def get(self, wallet: str, mint: str) -> WatchlistRecord | None:
        result = await self.session.execute(
            select(WatchlistRecord).where(WatchlistRecord.wallet == wallet, WatchlistRecord.mint == mint)
        )
        return result.scalar_one_or_none()

    async def add(self, wallet: str, mint: str) -> WatchlistRecord:
        record = WatchlistRecord(wallet=wallet, mint=mint)
        self.session.add(record)
        await self.session.flush()
        return record

    async def remove(self, wallet: str, mint: str) -> None:
        await self.session.execute(
            delete(WatchlistRecord).where(WatchlistRecord.wallet == wallet, WatchlistRecord.mint == mint)
        )


class NewsCacheRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_valid(self, cache_key: str, now) -> NewsCacheRecord | None:
        result = await self.session.execute(
            select(NewsCacheRecord).where(
                NewsCacheRecord.cache_key == cache_key,
                NewsCacheRecord.expires_at > now,
            )
        )
        return result.scalar_one_or_none()

    async def put(self, **payload: object) -> NewsCacheRecord:
        existing = await self.session.get(NewsCacheRecord, payload["cache_key"])
        if existing is None:
            existing = NewsCacheRecord(**payload)
            self.session.add(existing)
        else:
            for key, value in payload.items():
                setattr(existing, key, value)
        await self.session.flush()
        return existing

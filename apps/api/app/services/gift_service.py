from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import IdempotencyConflictError, NotFoundError, UnsupportedAssetError
from app.core.time import as_utc
from app.core.validators import require_recipient_reference, require_solana_address
from app.db.models import GiftClaimRecord
from app.db.repositories import AssetRepository
from app.schemas.gifts import GiftCreate, GiftResponse


class GiftService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.assets = AssetRepository(session)

    async def create(self, request: GiftCreate, idempotency_key: str) -> GiftResponse:
        require_solana_address(request.sender_wallet, field="sender_wallet")
        require_solana_address(request.asset_mint, field="asset_mint")
        recipient = require_recipient_reference(request.recipient_reference)
        asset = await self.assets.get_by_mint(request.asset_mint)
        if asset is None or not asset.verified or not asset.tradable:
            raise UnsupportedAssetError(request.asset_mint)
        existing = await self.session.scalar(
            select(GiftClaimRecord).where(
                GiftClaimRecord.sender_wallet == request.sender_wallet,
                GiftClaimRecord.idempotency_key == idempotency_key,
            )
        )
        if existing is not None:
            if (
                existing.asset_mint != request.asset_mint
                or existing.amount != request.amount
                or existing.recipient_reference != recipient
            ):
                raise IdempotencyConflictError()
            return self._to_response(existing)

        expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        record = GiftClaimRecord(
            claim_code=token_urlsafe(32),
            sender_wallet=request.sender_wallet,
            idempotency_key=idempotency_key,
            recipient_reference=recipient,
            asset_mint=request.asset_mint,
            amount=request.amount,
            status="pending",
            expires_at=expires_at,
        )
        self.session.add(record)
        await self.session.commit()
        return self._to_response(record)

    async def get(self, claim_id: str) -> GiftResponse:
        record = await self.session.scalar(select(GiftClaimRecord).where(GiftClaimRecord.claim_code == claim_id))
        if record is None:
            raise NotFoundError("gift claim")
        if record.status == "pending" and as_utc(record.expires_at) <= datetime.now(timezone.utc):
            record.status = "expired"
            await self.session.commit()
        return self._to_response(record)

    @staticmethod
    def _to_response(record: GiftClaimRecord) -> GiftResponse:
        return GiftResponse(
            claim_code=record.claim_code,
            asset_mint=record.asset_mint,
            amount=record.amount,
            recipient_reference=record.recipient_reference,
            status=record.status,
            expires_at=as_utc(record.expires_at),
        )

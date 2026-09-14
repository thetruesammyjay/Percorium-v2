import hashlib
import json
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.exceptions import AppError, IdempotencyConflictError, NotFoundError
from app.core.time import as_utc
from app.core.validators import require_solana_address, require_solana_signature
from app.db.models import TradeIntentRecord
from app.db.repositories import TradeIntentRepository
from app.integrations.alchemy import AlchemySolanaClient
from app.integrations.jupiter import JupiterClient
from app.lib.allowlist import AssetAllowlist
from app.schemas.common import RailName, TradeStatus
from app.schemas.quotes import QuoteRequest
from app.schemas.trades import TradeCreate, TradeListResponse, TradeResponse
from app.services.fee_service import FeeBreakdown, breakdown
from app.services.quote_service import QuoteService


class TradeService:
    def __init__(self, session: AsyncSession, settings: Settings, client: httpx.AsyncClient) -> None:
        self.session = session
        self.settings = settings
        self.trades = TradeIntentRepository(session)
        self.quotes = QuoteService(session, settings, client)
        self.jupiter = JupiterClient(settings, client)
        self.allowlist = AssetAllowlist(settings, client)
        self.alchemy = AlchemySolanaClient(settings.alchemy_solana_rpc_url, client)

    async def create_trade(self, request: TradeCreate, idempotency_key: str) -> TradeResponse:
        await self._validate_request(request)
        fingerprint = self._fingerprint(request)
        existing = await self.trades.get_by_idempotency(request.wallet, idempotency_key)
        if existing is not None:
            if existing.request_hash != fingerprint:
                raise IdempotencyConflictError()
            return self._to_response(existing)

        amount = int(request.sell_amount)
        fees = breakdown(amount, self.settings.platform_fee_bps, request.copy_master)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.settings.quote_ttl_seconds)
        if not self.quotes.execution_configured:
            return self._not_configured(request, fees, amount + fees.platform_fee, expires_at)

        quote = await self.quotes.create_quote(
            QuoteRequest(
                rail=request.rail,
                tab=request.tab,
                sell_mint=request.sell_mint,
                buy_mint=request.buy_mint,
                sell_amount=request.sell_amount,
                slippage_bps=request.slippage_bps,
                mode="exact_in",
            )
        )
        if quote.status != "ready" or not quote.provider_quote:
            return self._not_configured(request, fees, amount + fees.platform_fee, expires_at)

        swap = await self.jupiter.swap(
            wallet=request.wallet,
            quote_response=quote.provider_quote,
            platform_fee_bps=self.settings.platform_fee_bps,
            platform_fee_account=self.settings.platform_fee_wallet,
        )
        record = await self.trades.create(
            wallet=request.wallet,
            idempotency_key=idempotency_key,
            request_hash=fingerprint,
            rail=request.rail.value,
            tab=request.tab,
            sell_mint=request.sell_mint,
            buy_mint=request.buy_mint,
            sell_amount=request.sell_amount,
            expected_buy_amount=quote.expected_buy_amount,
            price_impact_bps=quote.price_impact_bps,
            fee_bps=self.settings.platform_fee_bps,
            platform_fee=quote.platform_fee,
            copy_master_fee=str(fees.copy_master_fee),
            percorium_fee=str(fees.percorium_fee),
            network_fee=quote.network_fee,
            total_debit=quote.total_debit,
            is_private=request.is_private,
            status=TradeStatus.AWAITING_SIGNATURE.value,
            transaction_payload=swap.transaction,
            expires_at=quote.expires_at,
            external_id=None,
        )
        await self.session.commit()
        return self._to_response(record)

    async def list_trades(self, wallet: str, limit: int = 50) -> TradeListResponse:
        require_solana_address(wallet, field="wallet")
        records = await self.trades.get_for_wallet(wallet, limit=limit)
        now = datetime.now(timezone.utc)
        changed = False
        for record in records:
            if record.status == TradeStatus.AWAITING_SIGNATURE.value and as_utc(record.expires_at) <= now:
                record.status = TradeStatus.EXPIRED.value
                changed = True
        if changed:
            await self.session.commit()
        return TradeListResponse(items=[self._to_response(record) for record in records])

    async def get_trade(self, record_id: str, wallet: str) -> TradeResponse:
        require_solana_address(wallet, field="wallet")
        record = await self.trades.get_by_id(record_id)
        if record is None:
            raise NotFoundError("trade intent")
        if record.wallet != wallet:
            raise AppError("The trade does not belong to this wallet.", code="wallet_mismatch", status_code=403)
        if record.status == TradeStatus.SUBMITTED.value and record.tx_signature and self.alchemy.configured:
            provider_status = await self.alchemy.get_signature_status(record.tx_signature)
            if provider_status in {TradeStatus.CONFIRMED.value, TradeStatus.FAILED.value}:
                record.status = provider_status
                await self.session.commit()
        return self._to_response(record)

    async def submit_trade(self, record_id: str, wallet: str, signature: str) -> TradeResponse:
        require_solana_address(wallet, field="wallet")
        require_solana_signature(signature)
        record = await self.trades.get_by_id(record_id)
        if record is None:
            raise NotFoundError("trade intent")
        if record.wallet != wallet:
            raise AppError("The trade does not belong to this wallet.", code="wallet_mismatch", status_code=403)
        if record.status != TradeStatus.AWAITING_SIGNATURE.value:
            return self._to_response(record)
        if as_utc(record.expires_at) <= datetime.now(timezone.utc):
            record.status = TradeStatus.EXPIRED.value
            await self.session.commit()
            return self._to_response(record)
        await self.trades.set_submitted(record, signature)
        await self.session.commit()
        return self._to_response(record)

    async def _validate_request(self, request: TradeCreate) -> None:
        if request.rail == RailName.BASE:
            if not self.settings.base_enabled:
                raise AppError(
                    "The Base rail is disabled.", code="rail_disabled", status_code=403, details={"rail": "base"}
                )
            raise AppError(
                "The Base rail adapter is not enabled in this Solana-first API build.",
                code="rail_not_implemented",
                status_code=501,
                details={"rail": "base"},
            )
        require_solana_address(request.sell_mint, field="sell_mint")
        require_solana_address(request.buy_mint, field="buy_mint")
        require_solana_address(request.wallet, field="wallet")
        await self.allowlist.assert_pair_allowed(request.sell_mint, request.buy_mint, request.tab)

    @staticmethod
    def _fingerprint(request: TradeCreate) -> str:
        canonical = json.dumps(request.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()

    def _not_configured(
        self, request: TradeCreate, fees: FeeBreakdown, total: int, expires_at: datetime
    ) -> TradeResponse:
        return TradeResponse(
            status="not_configured",
            rail=request.rail,
            tab=request.tab,
            wallet=request.wallet,
            sell_mint=request.sell_mint,
            buy_mint=request.buy_mint,
            sell_amount=request.sell_amount,
            fee_bps=fees.fee_bps,
            platform_fee=str(fees.platform_fee),
            copy_master_fee=str(fees.copy_master_fee),
            percorium_fee=str(fees.percorium_fee),
            total_debit=str(total),
            expires_at=expires_at,
            message="Configure Jupiter credentials and the Percorium fee wallet before preparing a transaction.",
        )

    @staticmethod
    def _to_response(record: TradeIntentRecord) -> TradeResponse:
        status = TradeStatus(record.status)
        return TradeResponse(
            id=record.id,
            status=status,
            rail=RailName(record.rail),
            tab=record.tab,
            wallet=record.wallet,
            sell_mint=record.sell_mint,
            buy_mint=record.buy_mint,
            sell_amount=record.sell_amount,
            expected_buy_amount=record.expected_buy_amount,
            price_impact_bps=record.price_impact_bps,
            fee_bps=record.fee_bps,
            platform_fee=record.platform_fee,
            copy_master_fee=record.copy_master_fee,
            percorium_fee=record.percorium_fee,
            network_fee=record.network_fee or "estimated",
            total_debit=record.total_debit,
            expires_at=as_utc(record.expires_at),
            transaction=record.transaction_payload,
            tx_signature=record.tx_signature,
            message="Wallet signature required."
            if status == TradeStatus.AWAITING_SIGNATURE
            else "Trade state updated.",
        )
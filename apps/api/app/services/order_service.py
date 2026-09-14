import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Literal, cast

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.exceptions import AppError, IdempotencyConflictError, NotFoundError
from app.core.time import as_utc
from app.core.validators import require_solana_address, require_solana_signature
from app.db.models import OrderIntentRecord
from app.db.repositories import OrderIntentRepository
from app.integrations.jupiter import JupiterClient
from app.lib.allowlist import AssetAllowlist
from app.schemas.common import OrderStatus, RailName
from app.schemas.orders import OrderCreate, OrderListResponse, OrderResponse
from app.services.fee_service import calculate_fee


class OrderService:
    def __init__(self, session: AsyncSession, settings: Settings, client: httpx.AsyncClient) -> None:
        self.session = session
        self.settings = settings
        self.orders = OrderIntentRepository(session)
        self.jupiter = JupiterClient(settings, client)
        self.allowlist = AssetAllowlist(settings, client)

    async def create_order(self, request: OrderCreate, idempotency_key: str) -> OrderResponse:
        await self._validate_request(request)
        fingerprint = self._fingerprint(request)
        existing = await self.orders.get_by_idempotency(request.wallet, idempotency_key)
        if existing is not None:
            if existing.request_hash != fingerprint:
                raise IdempotencyConflictError()
            return self._to_response(existing)

        amount = int(request.amount)
        platform_fee = calculate_fee(amount, self.settings.platform_fee_bps)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.settings.quote_ttl_seconds)
        if not (self.jupiter.configured and self.settings.platform_fee_wallet):
            return self._not_configured(request, platform_fee, amount + platform_fee, expires_at)

        require_solana_address(self.settings.platform_fee_wallet or "", field="platform_fee_wallet")
        provider_payload = {
            "user": request.wallet,
            "inputMint": request.input_mint,
            "outputMint": request.output_mint,
            "amount": request.amount,
            "orderType": request.order_type,
            "slippageBps": request.slippage_bps,
            "limitPrice": request.limit_price,
            "intervalSeconds": request.interval_seconds,
            "occurrences": request.occurrences,
            "platformFeeBps": self.settings.platform_fee_bps,
            "platformFeeWallet": self.settings.platform_fee_wallet,
        }
        instruction = await self.jupiter.create_trigger_order(provider_payload)
        provider_expiry = self._parse_expiry(instruction.expires_at, fallback=expires_at)
        expires_at = min(provider_expiry, expires_at)
        if expires_at <= datetime.now(timezone.utc):
            raise AppError(
                "Jupiter returned an expired order instruction.", code="provider_order_expired", status_code=502
            )

        record = await self.orders.create(
            wallet=request.wallet,
            idempotency_key=idempotency_key,
            request_hash=fingerprint,
            rail=request.rail.value,
            tab=request.tab,
            order_type=request.order_type,
            input_mint=request.input_mint,
            output_mint=request.output_mint,
            amount=request.amount,
            limit_price=request.limit_price,
            interval_seconds=request.interval_seconds,
            occurrences=request.occurrences,
            fee_bps=self.settings.platform_fee_bps,
            platform_fee=str(platform_fee),
            total_debit=str(amount + platform_fee),
            status=OrderStatus.AWAITING_SIGNATURE.value,
            transaction_payload=instruction.transaction,
            provider_order_id=instruction.provider_order_id,
            expires_at=expires_at,
        )
        await self.session.commit()
        return self._to_response(record)

    async def list_orders(self, wallet: str, limit: int = 50) -> OrderListResponse:
        require_solana_address(wallet, field="wallet")
        records = await self.orders.get_for_wallet(wallet, limit=limit)
        now = datetime.now(timezone.utc)
        changed = False
        for record in records:
            if record.status == OrderStatus.AWAITING_SIGNATURE.value and as_utc(record.expires_at) <= now:
                record.status = OrderStatus.EXPIRED.value
                changed = True
        if changed:
            await self.session.commit()
        return OrderListResponse(items=[self._to_response(record) for record in records])

    async def submit_order(self, record_id: str, wallet: str, signature: str) -> OrderResponse:
        require_solana_address(wallet, field="wallet")
        require_solana_signature(signature)
        record = await self.orders.get_by_id(record_id)
        if record is None:
            raise NotFoundError("order intent")
        if record.wallet != wallet:
            raise AppError("The order does not belong to this wallet.", code="wallet_mismatch", status_code=403)
        if record.status != OrderStatus.AWAITING_SIGNATURE.value:
            return self._to_response(record)
        if as_utc(record.expires_at) <= datetime.now(timezone.utc):
            record.status = OrderStatus.EXPIRED.value
            await self.session.commit()
            return self._to_response(record)
        await self.orders.set_submitted(record, signature)
        await self.session.commit()
        return self._to_response(record)

    async def _validate_request(self, request: OrderCreate) -> None:
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
        require_solana_address(request.wallet, field="wallet")
        require_solana_address(request.input_mint, field="input_mint")
        require_solana_address(request.output_mint, field="output_mint")
        await self.allowlist.assert_pair_allowed(request.input_mint, request.output_mint, request.tab)

    @staticmethod
    def _parse_expiry(value: str | None, fallback: datetime) -> datetime:
        if not value:
            return fallback
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise AppError(
                "Jupiter returned an invalid expiry.", code="provider_invalid_payload", status_code=502
            ) from exc
        return parsed.replace(tzinfo=parsed.tzinfo or timezone.utc)

    @staticmethod
    def _fingerprint(request: OrderCreate) -> str:
        canonical = json.dumps(request.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode()).hexdigest()

    def _not_configured(self, request: OrderCreate, fee: int, total: int, expires_at: datetime) -> OrderResponse:
        return OrderResponse(
            status="not_configured",
            rail=request.rail,
            tab=request.tab,
            wallet=request.wallet,
            order_type=request.order_type,
            input_mint=request.input_mint,
            output_mint=request.output_mint,
            amount=request.amount,
            limit_price=request.limit_price,
            interval_seconds=request.interval_seconds,
            occurrences=request.occurrences,
            fee_bps=self.settings.platform_fee_bps,
            platform_fee=str(fee),
            total_debit=str(total),
            expires_at=expires_at,
            message="Configure Jupiter credentials before preparing an order instruction.",
        )

    @staticmethod
    def _to_response(record: OrderIntentRecord) -> OrderResponse:
        status = OrderStatus(record.status)
        return OrderResponse(
            id=record.id,
            status=status,
            rail=RailName(record.rail),
            tab=record.tab,
            wallet=record.wallet,
            order_type=cast(Literal["limit", "dca"], record.order_type),
            input_mint=record.input_mint,
            output_mint=record.output_mint,
            amount=record.amount,
            limit_price=record.limit_price,
            interval_seconds=record.interval_seconds,
            occurrences=record.occurrences,
            fee_bps=record.fee_bps,
            platform_fee=record.platform_fee,
            total_debit=record.total_debit,
            expires_at=as_utc(record.expires_at),
            transaction=record.transaction_payload,
            provider_order_id=record.provider_order_id,
            tx_signature=record.tx_signature,
            message="Wallet signature required."
            if status == OrderStatus.AWAITING_SIGNATURE
            else "Order state updated.",
        )
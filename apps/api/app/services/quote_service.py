from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.exceptions import AppError, UnsupportedAssetError
from app.core.validators import require_solana_address
from app.db.repositories import AssetRepository
from app.integrations.sunrise import SunriseClient
from app.schemas.common import RailName
from app.schemas.quotes import QuoteRequest, QuoteResponse
from app.services.fee_service import calculate_fee


class QuoteService:
    def __init__(self, session: AsyncSession, settings: Settings, client: httpx.AsyncClient) -> None:
        self.session = session
        self.settings = settings
        self.assets = AssetRepository(session)
        self.sunrise = SunriseClient(settings, client)

    @property
    def execution_configured(self) -> bool:
        return self.sunrise.configured and bool(self.settings.platform_fee_wallet)

    async def create_quote(self, request: QuoteRequest) -> QuoteResponse:
        await self._validate_request(request)
        amount = int(request.sell_amount)
        platform_fee = calculate_fee(amount, self.settings.platform_fee_bps)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.settings.quote_ttl_seconds)
        if not self.execution_configured:
            return self._not_configured(request, platform_fee, amount + platform_fee, expires_at)

        require_solana_address(self.settings.platform_fee_wallet or "", field="platform_fee_wallet")
        upstream = await self.sunrise.quote(
            request,
            platform_fee_bps=self.settings.platform_fee_bps,
            platform_fee_wallet=self.settings.platform_fee_wallet,
        )
        provider_expiry = upstream.expires_at
        if provider_expiry.tzinfo is None:
            provider_expiry = provider_expiry.replace(tzinfo=timezone.utc)
        expires_at = min(provider_expiry, expires_at)
        if expires_at <= datetime.now(timezone.utc):
            raise AppError("Sunrise returned an expired quote.", code="provider_quote_expired", status_code=502)
        return QuoteResponse(
            status="ready",
            rail=request.rail,
            sell_mint=request.sell_mint,
            buy_mint=request.buy_mint,
            sell_amount=request.sell_amount,
            expected_buy_amount=upstream.expected_buy_amount,
            price_impact_bps=upstream.price_impact_bps,
            fee_bps=self.settings.platform_fee_bps,
            platform_fee=str(platform_fee),
            network_fee=upstream.network_fee,
            total_debit=str(amount + platform_fee),
            expires_at=expires_at,
            transaction=upstream.transaction,
            message=None,
        )

    def _not_configured(self, request: QuoteRequest, fee: int, total: int, expires_at: datetime) -> QuoteResponse:
        return QuoteResponse(
            status="not_configured",
            rail=request.rail,
            sell_mint=request.sell_mint,
            buy_mint=request.buy_mint,
            sell_amount=request.sell_amount,
            fee_bps=self.settings.platform_fee_bps,
            platform_fee=str(fee),
            total_debit=str(total),
            expires_at=expires_at,
            message="Configure Sunrise credentials and the Percorium fee wallet before requesting an executable quote.",
        )

    async def _validate_request(self, request: QuoteRequest) -> None:
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
        if request.sell_mint == request.buy_mint:
            raise AppError("sell_mint and buy_mint must be different.", code="same_asset", status_code=422)

        if self.sunrise.configured:
            for mint in (request.sell_mint, request.buy_mint):
                if mint in {self.settings.solana_usdc_mint, self.settings.solana_wrapped_sol_mint}:
                    continue
                asset = await self.assets.get_by_mint(mint)
                if asset is None or not asset.verified or not asset.tradable:
                    raise UnsupportedAssetError(mint)

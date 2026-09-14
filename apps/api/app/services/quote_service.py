from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.exceptions import AppError
from app.core.validators import require_solana_address
from app.integrations.jupiter import JupiterClient
from app.lib.allowlist import AssetAllowlist
from app.schemas.common import RailName
from app.schemas.quotes import QuoteRequest, QuoteResponse
from app.services.fee_service import calculate_fee


class QuoteService:
    def __init__(self, session: AsyncSession, settings: Settings, client: httpx.AsyncClient) -> None:
        self.session = session
        self.settings = settings
        self.jupiter = JupiterClient(settings, client)
        self.allowlist = AssetAllowlist(settings, client)

    @property
    def execution_configured(self) -> bool:
        return self.jupiter.configured and bool(self.settings.platform_fee_wallet)

    async def create_quote(self, request: QuoteRequest) -> QuoteResponse:
        await self._validate_request(request)
        amount = int(request.sell_amount)
        platform_fee = calculate_fee(amount, self.settings.platform_fee_bps)
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=self.settings.quote_ttl_seconds)
        if not self.execution_configured:
            return self._not_configured(request, platform_fee, amount + platform_fee, expires_at)

        require_solana_address(self.settings.platform_fee_wallet or "", field="platform_fee_wallet")
        upstream = await self.jupiter.quote(
            input_mint=request.sell_mint,
            output_mint=request.buy_mint,
            amount=request.sell_amount,
            slippage_bps=request.slippage_bps,
            platform_fee_bps=self.settings.platform_fee_bps,
        )
        return QuoteResponse(
            status="ready",
            rail=request.rail,
            tab=request.tab,
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
            transaction=None,
            provider_quote=upstream.raw_payload,
            message="Quote prepared by Jupiter. Review before signing.",
        )

    def _not_configured(self, request: QuoteRequest, fee: int, total: int, expires_at: datetime) -> QuoteResponse:
        return QuoteResponse(
            status="not_configured",
            rail=request.rail,
            tab=request.tab,
            sell_mint=request.sell_mint,
            buy_mint=request.buy_mint,
            sell_amount=request.sell_amount,
            fee_bps=self.settings.platform_fee_bps,
            platform_fee=str(fee),
            total_debit=str(total),
            expires_at=expires_at,
            message="Configure Jupiter credentials and the Percorium fee wallet before requesting an executable quote.",
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
        await self.allowlist.assert_pair_allowed(request.sell_mint, request.buy_mint, request.tab)
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from app.core.config import Settings
from app.integrations.jupiter_price import JupiterPriceClient
from app.integrations.jupiter_tokens import JupiterTokenClient
from app.schemas.market import MarketFeedResponse, MarketQuote


class CryptoMarketService:
    def __init__(self, settings: Settings, client: httpx.AsyncClient) -> None:
        self.settings = settings
        self.prices = JupiterPriceClient(settings, client)
        self.tokens = JupiterTokenClient(settings, client)

    async def get_feed(self, mints: str | None = None) -> MarketFeedResponse:
        requested = self._normalize_mints(mints or self.settings.crypto_feed_mints)
        fetched_at = datetime.now(timezone.utc)
        if not self.prices.configured:
            return MarketFeedResponse(
                items=[],
                symbols=[],
                configured=False,
                source="jupiter",
                fetched_at=fetched_at,
                message="Configure JUPITER_API_KEY to load live crypto prices.",
            )

        prices = await self.prices.prices(requested)
        metadata = await self.tokens.by_mints(requested)
        items: list[MarketQuote] = []
        for mint in requested:
            price = prices.get(mint)
            if not isinstance(price, dict):
                continue
            token = metadata.get(mint, {})
            symbol = self._text(token, "symbol") or mint[:6].upper()
            usd_price = price.get("usdPrice")
            if not isinstance(usd_price, (int, float)) or usd_price < 0:
                continue
            change = price.get("priceChange24h")
            change_percent = float(change) if isinstance(change, (int, float)) else 0.0
            items.append(
                MarketQuote(
                    symbol=symbol[:12],
                    mint=mint,
                    logo_url=self._text(token, "icon", "logoURI", "logo_url", "logoUrl"),
                    price=float(usd_price),
                    change=0.0,
                    change_percent=change_percent,
                    as_of=fetched_at,
                    source="jupiter",
                )
            )
        message = None if items else "Live crypto prices are temporarily unavailable from Jupiter."
        return MarketFeedResponse(
            items=items,
            symbols=[item.symbol for item in items],
            configured=True,
            source="jupiter",
            fetched_at=fetched_at,
            message=message,
        )

    @staticmethod
    def _normalize_mints(value: str) -> list[str]:
        return list(dict.fromkeys(item.strip() for item in value.split(",") if item.strip()))[:50]

    @staticmethod
    def _text(row: dict[str, Any], *keys: str) -> str | None:
        for key in keys:
            value = row.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None

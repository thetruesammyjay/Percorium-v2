import asyncio
from datetime import datetime, timezone
from typing import Any

import httpx

from app.core.config import Settings
from app.core.exceptions import AppError, IntegrationNotConfiguredError, ProviderRequestError
from app.integrations.finnhub import FinnhubClient
from app.schemas.market import MarketFeedResponse, MarketQuote


class MarketService:
    """Fetches a bounded set of live market quotes without inventing fallback values."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient) -> None:
        self.settings = settings
        self.finnhub = FinnhubClient(settings, client)

    async def get_feed(self, symbols: str | None = None) -> MarketFeedResponse:
        requested = self._normalize_symbols(symbols or self.settings.market_feed_symbols)
        fetched_at = datetime.now(timezone.utc)
        if not self.finnhub.configured:
            return MarketFeedResponse(
                items=[],
                symbols=requested,
                configured=False,
                fetched_at=fetched_at,
                message="Configure FINNHUB_API_KEY to load live market data.",
            )

        responses = await asyncio.gather(
            *(self.finnhub.quote(symbol) for symbol in requested),
            return_exceptions=True,
        )
        items: list[MarketQuote] = []
        failures = 0
        for symbol, response in zip(requested, responses, strict=True):
            if isinstance(response, (IntegrationNotConfiguredError, ProviderRequestError)):
                failures += 1
                continue
            if isinstance(response, Exception):
                failures += 1
                continue
            try:
                item = self._normalize_quote(symbol, response)
            except (AppError, ValueError, TypeError):
                failures += 1
                continue
            if item is not None:
                items.append(item)
            else:
                failures += 1

        message = None
        if not items:
            message = "Live market data is temporarily unavailable from Finnhub."
        elif failures:
            message = f"{failures} market quote{'' if failures == 1 else 's'} unavailable."
        return MarketFeedResponse(
            items=items,
            symbols=requested,
            configured=True,
            fetched_at=fetched_at,
            message=message,
        )

    @staticmethod
    def _normalize_symbols(value: str) -> list[str]:
        symbols: list[str] = []
        for raw in value.split(","):
            symbol = raw.strip().upper()
            if not symbol or symbol in symbols:
                continue
            if not symbol.isascii() or not symbol.replace(".", "").isalnum() or len(symbol) > 12:
                raise AppError("symbols must be valid ticker symbols.", code="invalid_symbols", status_code=422)
            symbols.append(symbol)
        if not symbols:
            raise AppError("At least one ticker symbol is required.", code="invalid_symbols", status_code=422)
        if len(symbols) > 8:
            raise AppError(
                "A maximum of eight ticker symbols may be requested.",
                code="invalid_symbols",
                status_code=422,
            )
        return symbols

    @staticmethod
    def _normalize_quote(symbol: str, payload: dict[str, Any]) -> MarketQuote | None:
        current = payload.get("c")
        if not isinstance(current, (int, float)) or current <= 0:
            return None
        change = payload.get("d")
        change_percent = payload.get("dp")
        if not isinstance(change, (int, float)):
            change = 0.0
        if not isinstance(change_percent, (int, float)):
            change_percent = 0.0
        timestamp = payload.get("t")
        as_of = datetime.fromtimestamp(timestamp, tz=timezone.utc) if isinstance(timestamp, (int, float)) else None
        return MarketQuote(
            symbol=symbol,
            price=float(current),
            change=float(change),
            change_percent=float(change_percent),
            high=MarketService._number_or_none(payload.get("h")),
            low=MarketService._number_or_none(payload.get("l")),
            open=MarketService._number_or_none(payload.get("o")),
            previous_close=MarketService._number_or_none(payload.get("pc")),
            as_of=as_of,
        )

    @staticmethod
    def _number_or_none(value: Any) -> float | None:
        return float(value) if isinstance(value, (int, float)) and value >= 0 else None
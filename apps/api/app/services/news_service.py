import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError, IntegrationNotConfiguredError
from app.db.repositories import NewsCacheRepository
from app.integrations.finnhub import FinnhubClient
from app.schemas.news import NewsItem, NewsResponse


class NewsService:
    def __init__(self, session: AsyncSession, settings, client: httpx.AsyncClient) -> None:
        self.session = session
        self.settings = settings
        self.cache = NewsCacheRepository(session)
        self.finnhub = FinnhubClient(settings, client)

    async def get(self, symbol: str | None, days: int = 7) -> NewsResponse:
        normalized = (symbol or "SPY").strip().upper()
        if not normalized.isascii() or not normalized.replace(".", "").isalnum() or len(normalized) > 12:
            raise AppError("symbol must be a valid ticker.", code="invalid_symbol", status_code=422)
        fallback = symbol is None
        cache_key = hashlib.sha256(f"news:{normalized}:{days}".encode()).hexdigest()
        now = datetime.now(timezone.utc)
        cached = await self.cache.get_valid(cache_key, now)
        if cached is not None:
            return NewsResponse(
                items=[NewsItem.model_validate(item) for item in json.loads(cached.payload_json)],
                configured=True,
                fallback_symbol=normalized if fallback else None,
                cached=True,
            )
        if not self.finnhub.configured:
            return NewsResponse(
                items=[],
                configured=False,
                fallback_symbol=normalized if fallback else None,
                cached=False,
            )

        try:
            company = await self.finnhub.company_news(normalized, days=days)
            earnings = await self.finnhub.earnings(normalized)
        except IntegrationNotConfiguredError:
            return NewsResponse(items=[], configured=False, fallback_symbol=normalized if fallback else None)

        items = self._normalize_company_news(normalized, company)
        items.extend(self._normalize_earnings(normalized, earnings))
        payload = [item.model_dump(mode="json") for item in items]
        await self.cache.put(
            cache_key=cache_key,
            symbol=normalized,
            category="company_and_earnings",
            payload_json=json.dumps(payload, separators=(",", ":")),
            expires_at=now + timedelta(minutes=5),
            fetched_at=now,
        )
        await self.session.commit()
        return NewsResponse(
            items=items,
            configured=True,
            fallback_symbol=normalized if fallback else None,
            cached=False,
        )

    @staticmethod
    def _normalize_company_news(symbol: str, payload: list[dict[str, Any]]) -> list[NewsItem]:
        items: list[NewsItem] = []
        for item in payload:
            headline = str(item.get("headline") or "").strip()
            url = str(item.get("url") or "").strip()
            if not headline or not url:
                continue
            timestamp = item.get("datetime")
            if not isinstance(timestamp, (int, float)):
                continue
            published_at = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            article_id = str(item.get("id") or hashlib.sha1(url.encode()).hexdigest())
            items.append(
                NewsItem(
                    id=f"{symbol.lower()}-{article_id}",
                    symbol=symbol,
                    headline=headline,
                    summary=str(item.get("summary") or "").strip() or None,
                    source=str(item.get("source") or "Finnhub"),
                    url=url,
                    published_at=published_at,
                    category="company",
                )
            )
        return items

    @staticmethod
    def _normalize_earnings(symbol: str, payload: list[dict[str, Any]]) -> list[NewsItem]:
        items: list[NewsItem] = []
        for item in payload[:12]:
            date_value = str(item.get("date") or "").strip()
            if not date_value:
                continue
            try:
                published_at = datetime.fromisoformat(date_value).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            quarter = item.get("quarter")
            year = item.get("year")
            label = f"{symbol} earnings"
            if quarter is not None and year is not None:
                label = f"{symbol} Q{quarter} {year} earnings"
            items.append(
                NewsItem(
                    id=f"{symbol.lower()}-earnings-{date_value}",
                    symbol=symbol,
                    headline=label,
                    summary="Earnings calendar data from Finnhub.",
                    source="Finnhub",
                    url="https://finnhub.io/",
                    published_at=published_at,
                    category="earnings",
                )
            )
        return items

import asyncio
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

_TECH_TERMS = (
    "artificial intelligence",
    "ai ",
    "semiconductor",
    "chip",
    "cloud",
    "cybersecurity",
    "data center",
    "developer",
    "internet",
    "robot",
    "software",
    "space",
    "technology",
    "tech ",
)


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

    async def get_feed(self, days: int = 7) -> NewsResponse:
        """Build the market-wide New feed from news and event calendars."""
        cache_key = f"news-feed:{days}"
        now = datetime.now(timezone.utc)
        cached = await self.cache.get_valid(cache_key, now)
        if cached is not None:
            return NewsResponse(
                items=[NewsItem.model_validate(item) for item in json.loads(cached.payload_json)],
                configured=True,
                cached=True,
            )
        if not self.finnhub.configured:
            return NewsResponse(
                items=[],
                configured=False,
                cached=False,
                message="Configure FINNHUB_API_KEY to load the New feed.",
            )

        start = now.date() - timedelta(days=days)
        end = now.date() + timedelta(days=14)
        market_result, ipo_result, earnings_result = await asyncio.gather(
            self.finnhub.market_news(),
            self.finnhub.ipo_calendar(start, end),
            self.finnhub.earnings_calendar(start, end),
            return_exceptions=True,
        )
        market_news = market_result if isinstance(market_result, list) else []
        ipo_calendar = ipo_result if isinstance(ipo_result, list) else []
        earnings_calendar = earnings_result if isinstance(earnings_result, list) else []

        items = self._normalize_market_feed(market_news, now - timedelta(days=days))
        items.extend(self._normalize_ipo_feed(ipo_calendar))
        items.extend(self._normalize_earnings_feed(earnings_calendar, self.settings.market_feed_symbols))
        items = self._dedupe_and_sort(items)[:40]
        failures = sum(not isinstance(result, list) for result in (market_result, ipo_result, earnings_result))
        message = None
        if not items and failures == 3:
            message = "The New feed is temporarily unavailable from Finnhub."
        elif failures:
            message = "Some New feed sources are temporarily unavailable."

        payload = [item.model_dump(mode="json") for item in items]
        await self.cache.put(
            cache_key=cache_key,
            symbol="MARKET",
            category="new_feed",
            payload_json=json.dumps(payload, separators=(",", ":")),
            expires_at=now + timedelta(minutes=5),
            fetched_at=now,
        )
        await self.session.commit()
        return NewsResponse(items=items, configured=True, cached=False, message=message)

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

    @classmethod
    def _normalize_market_feed(cls, payload: list[dict[str, Any]], cutoff: datetime) -> list[NewsItem]:
        candidates: list[tuple[int, datetime, NewsItem]] = []
        for item in payload:
            headline = cls._text(item.get("headline"))
            url = cls._text(item.get("url"))
            timestamp = item.get("datetime")
            if not headline or not url or not isinstance(timestamp, (int, float)):
                continue
            published_at = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            if published_at < cutoff:
                continue
            related = cls._text(item.get("related"))
            symbol = next((part.strip().upper() for part in (related or "").split(",") if part.strip()), "MARKET")
            summary = cls._text(item.get("summary")) or None
            search_text = f"{headline} {summary or ''} {related or ''}".lower()
            score = sum(search_text.count(term) for term in _TECH_TERMS)
            candidates.append(
                (
                    score,
                    published_at,
                    NewsItem(
                        id=f"market-{item.get('id') or hashlib.sha1(url.encode()).hexdigest()}",
                        symbol=symbol[:12],
                        headline=headline,
                        summary=summary,
                        source=cls._text(item.get("source")) or "Finnhub",
                        url=url,
                        published_at=published_at,
                        category="market",
                    ),
                )
            )
        tech = [candidate for candidate in candidates if candidate[0] > 0]
        selected = tech if len(tech) >= 3 else candidates
        ordered = sorted(selected, key=lambda candidate: (candidate[0], candidate[1]), reverse=True)
        return [item for _, _, item in ordered[:16]]

    @classmethod
    def _normalize_ipo_feed(cls, payload: list[dict[str, Any]]) -> list[NewsItem]:
        items: list[NewsItem] = []
        for item in payload[:16]:
            symbol = cls._text(item.get("symbol")) or "IPO"
            name = cls._text(item.get("name")) or symbol
            date_value = cls._text(item.get("date"))
            if not date_value:
                continue
            event_date = cls._parse_calendar_date(date_value)
            if event_date is None:
                continue
            exchange = cls._text(item.get("exchange"))
            status = cls._text(item.get("status"))
            headline = f"{name} ({symbol}) IPO"
            if status:
                headline += f" {status.lower()}"
            summary = f"{exchange} listing" if exchange else "Upcoming IPO calendar event"
            items.append(
                NewsItem(
                    id=f"ipo-{symbol.lower()}-{date_value}",
                    symbol=symbol[:12],
                    headline=headline,
                    summary=summary,
                    source="Finnhub IPO calendar",
                    url="https://finnhub.io/",
                    published_at=event_date,
                    category="ipo",
                )
            )
        return items

    @classmethod
    def _normalize_earnings_feed(cls, payload: list[dict[str, Any]], symbols: str) -> list[NewsItem]:
        allowed = {part.strip().upper() for part in symbols.split(",") if part.strip()}
        items: list[NewsItem] = []
        for item in payload:
            symbol = cls._text(item.get("symbol"))
            date_value = cls._text(item.get("date"))
            if not symbol or not date_value or (allowed and symbol.upper() not in allowed):
                continue
            event_date = cls._parse_calendar_date(date_value)
            if event_date is None:
                continue
            quarter = item.get("quarter")
            year = item.get("year")
            period = f" Q{quarter} {year}" if quarter is not None and year is not None else ""
            direction = "reported" if event_date <= datetime.now(timezone.utc) else "scheduled"
            hour = cls._text(item.get("hour"))
            timing = f" ({hour})" if hour else ""
            items.append(
                NewsItem(
                    id=f"earnings-{symbol.lower()}-{date_value}",
                    symbol=symbol[:12],
                    headline=f"{symbol}{period} earnings {direction}{timing}",
                    summary="Earnings calendar event from Finnhub.",
                    source="Finnhub earnings calendar",
                    url="https://finnhub.io/",
                    published_at=event_date,
                    category="earnings",
                )
            )
        return items[:24]

    @staticmethod
    def _dedupe_and_sort(items: list[NewsItem]) -> list[NewsItem]:
        unique: dict[str, NewsItem] = {}
        for item in items:
            unique[item.id] = item
        return sorted(unique.values(), key=lambda item: item.published_at, reverse=True)

    @staticmethod
    def _text(value: Any) -> str | None:
        return value.strip() if isinstance(value, str) and value.strip() else None

    @staticmethod
    def _parse_calendar_date(value: str) -> datetime | None:
        try:
            return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)
        except ValueError:
            return None

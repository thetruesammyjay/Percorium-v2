from datetime import datetime, timedelta, timezone

from app.services.news_service import NewsService


def test_market_feed_prefers_technology_stories_when_available() -> None:
    now = datetime.now(timezone.utc)
    payload = [
        {
            "id": 1,
            "headline": "AI chip maker announces a new data center partnership",
            "summary": "Technology investors react to the software and cloud expansion.",
            "source": "Tech Desk",
            "url": "https://example.com/tech-1",
            "datetime": now.timestamp(),
            "related": "NVDA",
        },
        {
            "id": 2,
            "headline": "Semiconductor and cloud shares lead the technology session",
            "source": "Tech Desk",
            "url": "https://example.com/tech-2",
            "datetime": (now - timedelta(hours=1)).timestamp(),
            "related": "MSFT",
        },
        {
            "id": 3,
            "headline": "Software company expands its cybersecurity platform",
            "source": "Tech Desk",
            "url": "https://example.com/tech-3",
            "datetime": (now - timedelta(hours=2)).timestamp(),
            "related": "AAPL",
        },
        {
            "id": 4,
            "headline": "Dollar and yen trade quietly in Asia",
            "source": "Markets Desk",
            "url": "https://example.com/forex",
            "datetime": (now - timedelta(hours=3)).timestamp(),
            "related": "",
        },
    ]

    items = NewsService._normalize_market_feed(payload, now - timedelta(days=1))

    assert [item.symbol for item in items] == ["NVDA", "MSFT", "AAPL"]
    assert all(item.category == "market" for item in items)


def test_new_feed_normalizes_ipo_and_earnings_events() -> None:
    ipo_items = NewsService._normalize_ipo_feed(
        [{"symbol": "TECH", "name": "Tech Systems", "date": "2026-09-25", "exchange": "NASDAQ"}]
    )
    earnings_items = NewsService._normalize_earnings_feed(
        [{"symbol": "NVDA", "date": "2026-09-22", "quarter": 3, "year": 2026, "hour": "amc"}],
        "NVDA,MSFT",
    )

    assert ipo_items[0].category == "ipo"
    assert "NASDAQ listing" in (ipo_items[0].summary or "")
    assert earnings_items[0].category == "earnings"
    assert earnings_items[0].headline == "NVDA Q3 2026 earnings scheduled (amc)"

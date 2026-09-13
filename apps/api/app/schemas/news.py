from datetime import datetime

from pydantic import Field

from app.schemas.common import APIModel


class NewsItem(APIModel):
    id: str
    symbol: str
    headline: str = Field(min_length=1, max_length=500)
    summary: str | None = None
    source: str
    url: str
    published_at: datetime
    category: str


class NewsResponse(APIModel):
    items: list[NewsItem]
    configured: bool
    fallback_symbol: str | None = None
    cached: bool = False

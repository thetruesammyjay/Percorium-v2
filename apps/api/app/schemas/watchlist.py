from datetime import datetime

from app.schemas.common import APIModel


class WatchlistItem(APIModel):
    mint: str
    created_at: datetime


class WatchlistResponse(APIModel):
    items: list[WatchlistItem]

from typing import Literal

from app.schemas.common import APIModel


class LeaderboardItem(APIModel):
    rank: int
    handle: str
    fills: int
    volume: str
    period: Literal["24h", "7d"]


class LeaderboardResponse(APIModel):
    items: list[LeaderboardItem]
    period: Literal["24h", "7d"]
    message: str | None = None

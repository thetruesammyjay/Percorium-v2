from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class RailHealth:
    name: str
    configured: bool
    enabled: bool


class TradingRail(Protocol):
    name: str

    async def health(self) -> RailHealth: ...

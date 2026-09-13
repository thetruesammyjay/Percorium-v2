from app.core.config import Settings
from app.rails.base import RailHealth


class SolanaRail:
    name = "solana"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def health(self) -> RailHealth:
        return RailHealth(
            name=self.name,
            configured=bool(self.settings.alchemy_solana_rpc_url and self.settings.sunrise_api_url),
            enabled=True,
        )

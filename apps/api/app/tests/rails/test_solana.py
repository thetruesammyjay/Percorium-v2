import pytest

from app.core.config import Settings
from app.rails.solana import SolanaRail


@pytest.mark.asyncio
async def test_solana_is_the_default_enabled_rail() -> None:
    health = await SolanaRail(Settings()).health()
    assert health.name == "solana"
    assert health.enabled is True

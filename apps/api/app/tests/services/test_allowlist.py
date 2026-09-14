import httpx
import pytest

from app.core.config import Settings
from app.core.exceptions import UnsupportedAssetError
from app.lib.allowlist import AssetAllowlist

OFFICIAL_MINT = "22222222222222222222222222222222"
NOT_AN_EQUITY_MINT = "33333333333333333333333333333333"


def test_sunrise_normalization_keeps_only_equity_like_rows() -> None:
    assets = AssetAllowlist._normalize_equities(
        [
            {"mint": OFFICIAL_MINT, "symbol": "PERC", "name": "Percorium ETF", "type": "ETF"},
            {"mint": NOT_AN_EQUITY_MINT, "symbol": "MEME", "name": "A token", "type": "meme"},
        ]
    )

    assert [asset.mint for asset in assets] == [OFFICIAL_MINT]
    assert assets[0].kind.value == "etf"
    assert assets[0].verified is True
    assert assets[0].tradable is True


@pytest.mark.asyncio
async def test_settlement_assets_bypass_provider_list_but_are_not_asset_entries() -> None:
    settings = Settings(sunrise_api_url=None)
    async with httpx.AsyncClient() as client:
        allowlist = AssetAllowlist(settings, client)
        await allowlist.assert_pair_allowed(
            settings.solana_wrapped_sol_mint,
            settings.solana_usdc_mint,
            "stocks",
        )
        with pytest.raises(UnsupportedAssetError):
            await allowlist.assert_asset_allowed(settings.solana_usdc_mint, "stocks")
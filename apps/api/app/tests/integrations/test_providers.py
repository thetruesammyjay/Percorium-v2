import httpx
import pytest

from app.core.config import Settings
from app.integrations.alchemy import AlchemySolanaClient
from app.integrations.sunrise import SunriseClient

SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGkZwyTDt1v"


@pytest.mark.asyncio
async def test_sunrise_token_list_is_normalized_and_authenticated() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer secret"
        return httpx.Response(
            200,
            json=[
                {"mint": SOL_MINT, "symbol": "SOL", "name": "Solana", "kind": "stock"},
                {"mint": USDC_MINT, "symbol": "USDC", "name": "USD Coin", "kind": "stablecoin"},
            ],
        )

    settings = Settings(sunrise_api_url="https://sunrise.test", sunrise_api_key="secret")
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await SunriseClient(settings, client).list_tokens()

    assert result[0]["symbol"] == "SOL"
    assert result[1]["kind"] == "stablecoin"


def test_alchemy_balances_are_aggregated_by_mint() -> None:
    balances = AlchemySolanaClient._parse_token_balances(
        {
            "value": [
                {
                    "account": {
                        "data": {
                            "parsed": {
                                "info": {
                                    "mint": USDC_MINT,
                                    "tokenAmount": {"amount": "10", "decimals": 6},
                                }
                            }
                        }
                    }
                },
                {
                    "account": {
                        "data": {
                            "parsed": {
                                "info": {
                                    "mint": USDC_MINT,
                                    "tokenAmount": {"amount": "5", "decimals": 6},
                                }
                            }
                        }
                    }
                },
            ]
        }
    )

    assert len(balances) == 1
    assert balances[0].raw_amount == "15"
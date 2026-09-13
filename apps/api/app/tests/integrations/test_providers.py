from datetime import datetime, timezone

import httpx
import pytest

from app.core.config import Settings
from app.integrations.alchemy import AlchemySolanaClient
from app.integrations.sunrise import SunriseClient
from app.schemas.quotes import QuoteRequest

SOL_MINT = "So11111111111111111111111111111111111111112"
USDC_MINT = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"


@pytest.mark.asyncio
async def test_sunrise_quote_is_normalized_and_authenticated() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer secret"
        return httpx.Response(
            200,
            json={
                "expected_buy_amount": "00123",
                "price_impact_bps": 42,
                "network_fee": "5000",
                "expires_at": "2030-01-01T00:00:30Z",
                "transaction": "base64-transaction",
            },
        )

    settings = Settings(sunrise_api_url="https://sunrise.test", sunrise_api_key="secret")
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await SunriseClient(settings, client).quote(
            QuoteRequest(sell_mint=SOL_MINT, buy_mint=USDC_MINT, sell_amount="1000000")
        )

    assert result.expected_buy_amount == "123"
    assert result.price_impact_bps == 42
    assert result.transaction == "base64-transaction"
    assert result.expires_at == datetime(2030, 1, 1, 0, 0, 30, tzinfo=timezone.utc)


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

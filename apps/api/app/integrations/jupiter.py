from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any

import httpx

from app.core.config import Settings
from app.core.exceptions import IntegrationNotConfiguredError, ProviderRequestError
from app.integrations.http import get_json, post_json
from app.schemas.common import normalize_atomic_amount


@dataclass(frozen=True)
class JupiterQuote:
    expected_buy_amount: str
    price_impact_bps: int
    network_fee: str
    raw_payload: dict[str, Any]


@dataclass(frozen=True)
class JupiterSwapInstruction:
    transaction: str
    last_valid_block_height: int | None = None


@dataclass(frozen=True)
class JupiterOrderInstruction:
    transaction: str | None
    provider_order_id: str | None
    expires_at: str | None


class JupiterClient:
    name = "jupiter"

    def __init__(self, settings: Settings, client: httpx.AsyncClient) -> None:
        self.settings = settings
        self.client = client

    @property
    def configured(self) -> bool:
        return bool(self.settings.jupiter_api_key)

    def _require_configured(self) -> str:
        if not self.configured:
            raise IntegrationNotConfiguredError(self.name)
        return self.settings.jupiter_api_url.rstrip("/")

    def _headers(self, bearer_token: str | None = None) -> dict[str, str]:
        headers = {
            "x-api-key": self.settings.jupiter_api_key or "",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"
        return headers

    async def quote(
        self,
        *,
        input_mint: str,
        output_mint: str,
        amount: str,
        slippage_bps: int,
        platform_fee_bps: int = 0,
    ) -> JupiterQuote:
        base_url = self._require_configured()
        params: dict[str, Any] = {
            "inputMint": input_mint,
            "outputMint": output_mint,
            "amount": amount,
            "slippageBps": slippage_bps,
        }
        if platform_fee_bps > 0:
            params["platformFeeBps"] = platform_fee_bps
        response = await get_json(
            self.client,
            integration=self.name,
            url=f"{base_url}{self.settings.jupiter_quote_path}",
            headers=self._headers(),
            params=params,
        )
        if not isinstance(response, dict):
            raise ProviderRequestError(self.name, "Jupiter returned an invalid quote payload.")
        try:
            expected = normalize_atomic_amount(str(response["outAmount"]))
        except (KeyError, TypeError, ValueError) as exc:
            raise ProviderRequestError(self.name, "Jupiter returned an invalid output amount.") from exc
        price_impact_bps = self._price_impact_bps(response.get("priceImpactPct"))
        return JupiterQuote(
            expected_buy_amount=expected,
            price_impact_bps=price_impact_bps,
            network_fee="estimated",
            raw_payload=response,
        )

    async def swap(
        self,
        *,
        wallet: str,
        quote_response: dict[str, Any],
        platform_fee_bps: int,
        platform_fee_account: str | None,
    ) -> JupiterSwapInstruction:
        base_url = self._require_configured()
        payload: dict[str, Any] = {
            "userPublicKey": wallet,
            "quoteResponse": quote_response,
            "dynamicComputeUnitLimit": True,
            "prioritizationFeeLamports": "auto",
        }
        if platform_fee_account:
            # Jupiter requires an initialized token account for the input or output mint.
            payload["feeAccount"] = platform_fee_account
        response = await post_json(
            self.client,
            integration=self.name,
            url=f"{base_url}{self.settings.jupiter_swap_path}",
            headers=self._headers(),
            payload=payload,
        )
        if not isinstance(response, dict) or not isinstance(response.get("swapTransaction"), str):
            raise ProviderRequestError(self.name, "Jupiter returned an invalid swap transaction.")
        last_valid = response.get("lastValidBlockHeight")
        return JupiterSwapInstruction(
            transaction=response["swapTransaction"],
            last_valid_block_height=int(last_valid) if isinstance(last_valid, int) else None,
        )

    async def create_trigger_order(
        self, payload: dict[str, Any], *, bearer_token: str | None = None
    ) -> JupiterOrderInstruction:
        url = f"{self._require_configured()}{self.settings.jupiter_trigger_create_path}"
        response = await post_json(
            self.client,
            integration=self.name,
            url=url,
            payload={key: value for key, value in payload.items() if value is not None},
            headers=self._headers(bearer_token),
        )
        if not isinstance(response, dict):
            raise ProviderRequestError(self.name, "Jupiter returned an invalid order payload.")
        transaction = response.get("transaction") or response.get("tx")
        provider_order_id = response.get("order_id") or response.get("orderId") or response.get("id")
        expires_at = response.get("expires_at") or response.get("expiresAt")
        if transaction is not None and not isinstance(transaction, str):
            raise ProviderRequestError(self.name, "Jupiter returned an invalid transaction.")
        if provider_order_id is not None:
            provider_order_id = str(provider_order_id)
        if expires_at is not None:
            expires_at = str(expires_at)
        return JupiterOrderInstruction(
            transaction=transaction,
            provider_order_id=provider_order_id,
            expires_at=expires_at,
        )

    @staticmethod
    def _price_impact_bps(value: Any) -> int:
        if value is None:
            return 0
        try:
            pct = Decimal(str(value))
        except (InvalidOperation, ValueError):
            return 0
        return max(0, int(pct * Decimal("100")))
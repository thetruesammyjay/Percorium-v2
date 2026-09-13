from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx
from pydantic import TypeAdapter, ValidationError

from app.core.config import Settings
from app.core.exceptions import IntegrationNotConfiguredError, ProviderRequestError
from app.integrations.http import get_json, post_json
from app.schemas.assets import Asset
from app.schemas.common import normalize_atomic_amount
from app.schemas.quotes import QuoteRequest


@dataclass(frozen=True)
class SunriseQuote:
    expected_buy_amount: str
    price_impact_bps: int
    network_fee: str
    expires_at: datetime
    transaction: str | None
    external_id: str | None


class SunriseClient:
    name = "sunrise"

    def __init__(self, settings: Settings, client: httpx.AsyncClient) -> None:
        self.settings = settings
        self.client = client

    @property
    def configured(self) -> bool:
        return bool(self.settings.sunrise_api_url and self.settings.sunrise_api_key)

    def _require_configured(self) -> str:
        if not self.configured:
            raise IntegrationNotConfiguredError(self.name)
        return self.settings.sunrise_api_url.rstrip("/")  # type: ignore[union-attr]

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.settings.sunrise_api_key}",
            "Accept": "application/json",
        }

    async def list_assets(self, query: str | None = None) -> list[Asset]:
        base_url = self._require_configured()
        payload = await get_json(
            self.client,
            integration=self.name,
            url=f"{base_url}{self.settings.sunrise_assets_path}",
            headers=self._headers(),
            params={"query": query} if query else None,
        )
        raw_items: Any = payload.get("items", payload.get("data", payload)) if isinstance(payload, dict) else payload
        try:
            return TypeAdapter(list[Asset]).validate_python(raw_items)
        except ValidationError as exc:
            raise ProviderRequestError(self.name, "Sunrise returned an invalid asset payload.") from exc

    async def quote(
        self,
        request: QuoteRequest,
        *,
        platform_fee_bps: int | None = None,
        platform_fee_wallet: str | None = None,
    ) -> SunriseQuote:
        base_url = self._require_configured()
        provider_payload = request.model_dump(mode="json")
        if platform_fee_bps is not None:
            provider_payload["platform_fee_bps"] = platform_fee_bps
        if platform_fee_wallet is not None:
            provider_payload["platform_fee_wallet"] = platform_fee_wallet
        payload = await post_json(
            self.client,
            integration=self.name,
            url=f"{base_url}{self.settings.sunrise_quote_path}",
            headers=self._headers(),
            payload=provider_payload,
        )
        if not isinstance(payload, dict):
            raise ProviderRequestError(self.name, "Sunrise returned an invalid quote payload.")
        transaction = payload.get("transaction")
        if transaction is not None and not isinstance(transaction, str):
            raise ProviderRequestError(self.name, "Sunrise returned an invalid transaction payload.")
        external_id = payload.get("external_id")
        if external_id is not None and not isinstance(external_id, str):
            external_id = str(external_id)
        try:
            return SunriseQuote(
                expected_buy_amount=normalize_atomic_amount(str(payload["expected_buy_amount"])),
                price_impact_bps=max(0, int(payload.get("price_impact_bps", 0))),
                network_fee=str(payload.get("network_fee", "estimated")),
                expires_at=datetime.fromisoformat(str(payload["expires_at"]).replace("Z", "+00:00")),
                transaction=transaction,
                external_id=external_id,
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ProviderRequestError(self.name, "Sunrise returned an invalid quote payload.") from exc

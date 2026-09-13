from dataclasses import dataclass
from typing import Any

import httpx

from app.core.config import Settings
from app.core.exceptions import IntegrationNotConfiguredError, ProviderRequestError
from app.integrations.http import post_json


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

    async def create_trigger_order(self, payload: dict[str, Any]) -> JupiterOrderInstruction:
        url = f"{self._require_configured()}{self.settings.jupiter_trigger_create_path}"
        response = await post_json(
            self.client,
            integration=self.name,
            url=url,
            payload={key: value for key, value in payload.items() if value is not None},
            headers={
                "Authorization": f"Bearer {self.settings.jupiter_api_key}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
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

from __future__ import annotations

from typing import Any

import httpx

from app.core.config import Settings
from app.core.exceptions import IntegrationNotConfiguredError, ProviderRequestError
from app.integrations.http import get_json


class JupiterPriceClient:
    name = "jupiter_price"

    def __init__(self, settings: Settings, client: httpx.AsyncClient) -> None:
        self.settings = settings
        self.client = client

    @property
    def configured(self) -> bool:
        return bool(self.settings.jupiter_api_key)

    async def prices(self, mints: list[str]) -> dict[str, dict[str, Any]]:
        if not self.configured:
            raise IntegrationNotConfiguredError(self.name)
        if not mints:
            return {}
        payload = await get_json(
            self.client,
            integration=self.name,
            url=f"{self.settings.jupiter_api_url.rstrip('/')}{self.settings.jupiter_price_path}",
            headers={"Accept": "application/json", "x-api-key": self.settings.jupiter_api_key or ""},
            params={"ids": ",".join(mints)},
        )
        if not isinstance(payload, dict):
            raise ProviderRequestError(self.name, "Jupiter returned an invalid price payload.")
        return {str(key): value for key, value in payload.items() if isinstance(value, dict)}

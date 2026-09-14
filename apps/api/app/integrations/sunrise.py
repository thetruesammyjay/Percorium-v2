from typing import Any

import httpx
from pydantic import TypeAdapter, ValidationError

from app.core.config import Settings
from app.core.exceptions import IntegrationNotConfiguredError, ProviderRequestError
from app.integrations.http import get_json
from app.schemas.assets import Asset


class SunriseClient:
    """Sunrise token-list boundary used only to build the official allowlist."""

    name = "sunrise"

    def __init__(self, settings: Settings, client: httpx.AsyncClient) -> None:
        self.settings = settings
        self.client = client

    def _require_list_configured(self) -> str:
        if not self.settings.sunrise_api_url:
            raise IntegrationNotConfiguredError(self.name)
        return self.settings.sunrise_api_url.rstrip("/")

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.settings.sunrise_api_key:
            headers["Authorization"] = f"Bearer {self.settings.sunrise_api_key}"
        return headers

    async def list_tokens(self, query: str | None = None) -> list[dict[str, Any]]:
        base_url = self._require_list_configured()
        payload = await get_json(
            self.client,
            integration=self.name,
            url=f"{base_url}{self.settings.sunrise_list_tokens_path}",
            headers=self._headers(),
            params={"query": query} if query else None,
        )
        raw_items: Any = payload
        if isinstance(payload, dict):
            raw_items = payload.get("items", payload.get("data", payload.get("tokens", payload)))
        if not isinstance(raw_items, list):
            raise ProviderRequestError(self.name, "Sunrise returned an invalid token list payload.")
        return [item for item in raw_items if isinstance(item, dict)]

    async def list_assets(self, query: str | None = None) -> list[Asset]:
        try:
            return TypeAdapter(list[Asset]).validate_python(await self.list_tokens(query))
        except ValidationError as exc:
            raise ProviderRequestError(self.name, "Sunrise returned an invalid asset payload.") from exc
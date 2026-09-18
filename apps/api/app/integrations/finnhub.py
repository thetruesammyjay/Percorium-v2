from datetime import date, timedelta
from typing import Any

import httpx

from app.core.config import Settings
from app.core.exceptions import IntegrationNotConfiguredError, ProviderRequestError
from app.integrations.http import get_json


class FinnhubClient:
    name = "finnhub"

    def __init__(self, settings: Settings, client: httpx.AsyncClient) -> None:
        self.settings = settings
        self.client = client

    @property
    def configured(self) -> bool:
        return bool(self.settings.finnhub_api_key)

    async def quote(self, symbol: str) -> dict[str, Any]:
        """Return the latest quote payload for a US ticker from Finnhub."""
        if not self.configured:
            raise IntegrationNotConfiguredError(self.name)
        payload = await get_json(
            self.client,
            integration=self.name,
            url=f"{self.settings.finnhub_api_url.rstrip('/')}/quote",
            params={"symbol": symbol.upper(), "token": self.settings.finnhub_api_key},
        )
        if not isinstance(payload, dict):
            raise ProviderRequestError(self.name, "Finnhub returned an invalid quote payload.")
        return payload

    async def company_profile(self, symbol: str) -> dict[str, Any]:
        """Return Finnhub's company profile, including its published logo URL."""
        if not self.configured:
            raise IntegrationNotConfiguredError(self.name)
        payload = await get_json(
            self.client,
            integration=self.name,
            url=f"{self.settings.finnhub_api_url.rstrip('/')}/stock/profile2",
            params={"symbol": symbol.upper(), "token": self.settings.finnhub_api_key},
        )
        if not isinstance(payload, dict):
            raise ProviderRequestError(self.name, "Finnhub returned an invalid company profile payload.")
        return payload

    async def company_news(self, symbol: str, days: int = 7) -> list[dict[str, Any]]:
        if not self.configured:
            raise IntegrationNotConfiguredError(self.name)
        end = date.today()
        start = end - timedelta(days=days)
        payload = await get_json(
            self.client,
            integration=self.name,
            url=f"{self.settings.finnhub_api_url.rstrip('/')}/company-news",
            params={
                "symbol": symbol.upper(),
                "from": start.isoformat(),
                "to": end.isoformat(),
                "token": self.settings.finnhub_api_key,
            },
        )
        if not isinstance(payload, list):
            raise ProviderRequestError(self.name, "Finnhub returned an invalid news payload.")
        return [item for item in payload if isinstance(item, dict)]

    async def earnings(self, symbol: str) -> list[dict[str, Any]]:
        if not self.configured:
            raise IntegrationNotConfiguredError(self.name)
        payload = await get_json(
            self.client,
            integration=self.name,
            url=f"{self.settings.finnhub_api_url.rstrip('/')}/calendar/earnings",
            params={"symbol": symbol.upper(), "token": self.settings.finnhub_api_key},
        )
        if not isinstance(payload, dict) or not isinstance(payload.get("earningsCalendar"), list):
            raise ProviderRequestError(self.name, "Finnhub returned an invalid earnings payload.")
        return [item for item in payload["earningsCalendar"] if isinstance(item, dict)]

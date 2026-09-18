from __future__ import annotations

import asyncio
from typing import Any

import httpx

from app.core.config import Settings
from app.core.exceptions import IntegrationNotConfiguredError, ProviderRequestError
from app.integrations.http import get_json


class JupiterTokenClient:
    """Jupiter Tokens API boundary for operator-selected Solana mints."""

    name = "jupiter_tokens"

    def __init__(self, settings: Settings, client: httpx.AsyncClient) -> None:
        self.settings = settings
        self.client = client

    @property
    def configured(self) -> bool:
        return bool(self.settings.jupiter_api_key)

    def _headers(self) -> dict[str, str]:
        if not self.configured:
            raise IntegrationNotConfiguredError(self.name)
        return {"Accept": "application/json", "x-api-key": self.settings.jupiter_api_key or ""}

    async def search(self, query: str) -> list[dict[str, Any]]:
        payload = await get_json(
            self.client,
            integration=self.name,
            url=f"{self.settings.jupiter_api_url.rstrip('/')}{self.settings.jupiter_tokens_path}",
            headers=self._headers(),
            params={"query": query},
        )
        if not isinstance(payload, list):
            raise ProviderRequestError(self.name, "Jupiter returned an invalid token search payload.")
        return [item for item in payload if isinstance(item, dict)]

    async def by_mints(self, mints: list[str]) -> dict[str, dict[str, Any]]:
        if not mints:
            return {}
        responses = await asyncio.gather(*(self.search(mint) for mint in mints), return_exceptions=True)
        result: dict[str, dict[str, Any]] = {}
        for mint, response in zip(mints, responses, strict=True):
            if isinstance(response, Exception):
                continue
            for token in response:
                token_id = token.get("id") or token.get("address") or token.get("mint")
                if token_id == mint:
                    result[mint] = token
                    break
        return result

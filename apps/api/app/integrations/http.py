from collections.abc import Mapping
from typing import Any

import httpx

from app.core.exceptions import ProviderRequestError


async def get_json(
    client: httpx.AsyncClient,
    *,
    integration: str,
    url: str,
    headers: Mapping[str, str] | None = None,
    params: Mapping[str, Any] | None = None,
) -> Any:
    try:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise ProviderRequestError(integration) from exc


async def post_json(
    client: httpx.AsyncClient,
    *,
    integration: str,
    url: str,
    payload: Mapping[str, Any],
    headers: Mapping[str, str] | None = None,
) -> Any:
    try:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise ProviderRequestError(integration) from exc

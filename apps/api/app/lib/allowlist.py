from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Literal

import httpx

from app.core.config import Settings
from app.core.exceptions import AppError, ProviderRequestError, UnsupportedAssetError
from app.core.validators import require_solana_address
from app.integrations.http import get_json
from app.integrations.sunrise import SunriseClient
from app.schemas.assets import Asset
from app.schemas.common import AssetKind

AllowlistTab = Literal["stocks", "pre-ipo"]


@dataclass(frozen=True)
class _CacheEntry:
    expires_at: float
    assets: tuple[Asset, ...]


_CACHE: dict[str, _CacheEntry] = {}


class AssetAllowlist:
    """The only mint source accepted by trade, quote, and Trigger preparation."""

    def __init__(self, settings: Settings, client: httpx.AsyncClient) -> None:
        self.settings = settings
        self.client = client
        self.sunrise = SunriseClient(settings, client)

    @property
    def stocks_configured(self) -> bool:
        return bool(self.settings.sunrise_api_url)

    @property
    def preipo_configured(self) -> bool:
        return bool(self.settings.preipo_api_url)

    async def load_stocks(self) -> list[Asset]:
        cached = self._cached("stocks")
        if cached is not None:
            return cached
        if not self.stocks_configured:
            return self._store("stocks", [])
        assets = self._normalize_equities(await self.sunrise.list_tokens())
        return self._store("stocks", assets)

    async def load_preipo(self) -> list[Asset]:
        cached = self._cached("pre-ipo")
        if cached is not None:
            return cached
        if not self.preipo_configured:
            return self._store("pre-ipo", [])
        try:
            payload = await get_json(
                self.client,
                integration="prestocks",
                url=self.settings.preipo_api_url,
                headers={"Accept": "application/json"},
            )
        except ProviderRequestError:
            return self._store("pre-ipo", [])
        return self._store("pre-ipo", self._normalize_preipo(payload))

    async def load(self, tab: AllowlistTab) -> list[Asset]:
        return await self.load_stocks() if tab == "stocks" else await self.load_preipo()

    async def is_allowed(self, mint: str, tab: AllowlistTab) -> bool:
        if self.is_settlement(mint):
            return True
        return any(asset.mint == mint for asset in await self.load(tab))

    async def assert_asset_allowed(self, mint: str, tab: AllowlistTab) -> None:
        require_solana_address(mint, field="mint")
        if not await self.is_allowed(mint, tab) or self.is_settlement(mint):
            raise UnsupportedAssetError(mint)

    async def assert_pair_allowed(self, input_mint: str, output_mint: str, tab: AllowlistTab) -> None:
        require_solana_address(input_mint, field="input_mint")
        require_solana_address(output_mint, field="output_mint")
        if input_mint == output_mint:
            raise AppError("input_mint and output_mint must be different.", code="same_asset", status_code=422)
        allowed = {asset.mint for asset in await self.load(tab)}
        for field, mint in (("input_mint", input_mint), ("output_mint", output_mint)):
            if not self.is_settlement(mint) and mint not in allowed:
                raise UnsupportedAssetError(mint)

    def is_settlement(self, mint: str) -> bool:
        return mint in {
            self.settings.solana_usdc_mint,
            self.settings.solana_wrapped_sol_mint,
            self.settings.solana_usdt_mint,
        }

    def _cached(self, tab: str) -> list[Asset] | None:
        entry = _CACHE.get(self._cache_key(tab))
        if entry is None or entry.expires_at <= time.monotonic():
            return None
        return list(entry.assets)

    def _store(self, tab: str, assets: list[Asset]) -> list[Asset]:
        _CACHE[self._cache_key(tab)] = _CacheEntry(
            expires_at=time.monotonic() + self.settings.allowlist_cache_seconds,
            assets=tuple(assets),
        )
        return assets

    def _cache_key(self, tab: str) -> str:
        source = self.settings.sunrise_api_url if tab == "stocks" else self.settings.preipo_api_url
        return f"{tab}:{source or 'unconfigured'}"

    @staticmethod
    def _normalize_equities(rows: list[dict[str, Any]]) -> list[Asset]:
        assets: list[Asset] = []
        seen: set[str] = set()
        for row in rows:
            kind = AssetAllowlist._text(row, "kind", "type", "asset_type", "assetType", "category", "assetClass")
            kind_normalized = (kind or "").lower().replace("_", "-")
            if "stock" not in kind_normalized and "equity" not in kind_normalized and "etf" not in kind_normalized:
                continue
            mint = AssetAllowlist._text(row, "mint", "address", "tokenAddress", "token_address")
            if not mint or mint in seen:
                continue
            try:
                require_solana_address(mint, field="mint")
            except AppError:
                continue
            symbol = AssetAllowlist._text(row, "symbol", "ticker", "tokenSymbol") or mint[:6].upper()
            name = AssetAllowlist._text(row, "name", "companyName", "company", "title") or symbol
            logo_url = AssetAllowlist._text(row, "logo_url", "logoUrl", "image", "imageUrl")
            assets.append(
                Asset(
                    mint=mint,
                    symbol=symbol[:24],
                    name=name[:160],
                    kind=AssetKind.ETF if "etf" in kind_normalized else AssetKind.STOCK,
                    logo_url=logo_url,
                    verified=True,
                    tradable=True,
                )
            )
            seen.add(mint)
        return assets

    @staticmethod
    def _normalize_preipo(payload: Any) -> list[Asset]:
        rows = AssetAllowlist._rows(payload)
        assets: list[Asset] = []
        seen: set[str] = set()
        for row in rows:
            mint = AssetAllowlist._text(
                row,
                "mint",
                "address",
                "tokenAddress",
                "token_address",
                "contractAddress",
                "contract_address",
            )
            if not mint or mint in seen:
                continue
            try:
                require_solana_address(mint, field="mint")
            except AppError:
                continue
            symbol = AssetAllowlist._text(row, "symbol", "ticker", "tokenSymbol") or mint[:6].upper()
            name = AssetAllowlist._text(row, "name", "companyName", "company", "title") or symbol
            logo_url = AssetAllowlist._text(row, "logo_url", "logoUrl", "image", "imageUrl")
            assets.append(
                Asset(
                    mint=mint,
                    symbol=symbol[:24],
                    name=name[:160],
                    kind=AssetKind.STOCK,
                    logo_url=logo_url,
                    verified=True,
                    tradable=True,
                )
            )
            seen.add(mint)
        return assets

    @staticmethod
    def _rows(payload: Any) -> list[dict[str, Any]]:
        if isinstance(payload, list):
            return [row for row in payload if isinstance(row, dict)]
        if isinstance(payload, dict):
            for key in ("items", "data", "tokens", "stocks", "products", "prestocks"):
                value = payload.get(key)
                if isinstance(value, list):
                    return [row for row in value if isinstance(row, dict)]
        return []

    @staticmethod
    def _text(row: dict[str, Any], *keys: str) -> str | None:
        for key in keys:
            value = row.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None
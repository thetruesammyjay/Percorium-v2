from __future__ import annotations

import csv
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import httpx

from app.core.config import Settings
from app.core.exceptions import AppError, ProviderRequestError, UnsupportedAssetError
from app.core.validators import require_solana_address
from app.integrations.http import get_json
from app.integrations.jupiter_tokens import JupiterTokenClient
from app.schemas.assets import Asset
from app.schemas.common import AssetKind

AllowlistTab = Literal["stocks", "pre-ipo", "new"]


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
        self.jupiter_tokens = JupiterTokenClient(settings, client)

    @property
    def stocks_configured(self) -> bool:
        return bool(
            self._split_mints(self.settings.jupiter_stock_mints)
            or self._split_mints(self.settings.jupiter_etf_mints)
        )

    @property
    def preipo_configured(self) -> bool:
        return bool(self.settings.preipo_api_url and self.settings.preipo_pinned_mints.strip())

    @property
    def new_configured(self) -> bool:
        return bool(self.settings.new_launches_file)

    async def load_stocks(self) -> list[Asset]:
        cached = self._cached("stocks")
        if cached is not None:
            return cached
        if not self.stocks_configured:
            return self._store("stocks", [])
        stock_mints = self._split_mints(self.settings.jupiter_stock_mints)
        etf_mints = self._split_mints(self.settings.jupiter_etf_mints)
        all_mints = stock_mints + [mint for mint in etf_mints if mint not in stock_mints]
        metadata = await self.jupiter_tokens.by_mints(all_mints) if self.jupiter_tokens.configured else {}
        registry = self._load_registry()
        assets = self._normalize_operator_mints(metadata, stock_mints, AssetKind.STOCK, registry)
        assets.extend(self._normalize_operator_mints(metadata, etf_mints, AssetKind.ETF, registry))
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
        pins = {mint.strip() for mint in self.settings.preipo_pinned_mints.split(",") if mint.strip()}
        return self._store("pre-ipo", [asset for asset in self._normalize_preipo(payload) if asset.mint in pins])

    async def load_new(self) -> list[Asset]:
        # Only an operator-owned index can admit launches; clients cannot add mints.
        if not self.settings.new_launches_file:
            return []
        try:
            rows = json.loads(Path(self.settings.new_launches_file).read_text(encoding="utf-8"))
            assets = [Asset.model_validate(row) for row in rows]
        except (OSError, ValueError, TypeError) as exc:
            raise AppError(
                "The launch index is unavailable.", code="launch_index_unavailable", status_code=503
            ) from exc
        return sorted(
            [asset.model_copy(update={"verified": False}) for asset in assets if asset.kind == AssetKind.MEMESTOCK],
            key=lambda asset: not asset.featured,
        )

    async def load(self, tab: AllowlistTab) -> list[Asset]:
        if tab == "stocks":
            return await self.load_stocks()
        if tab == "pre-ipo":
            return await self.load_preipo()
        return await self.load_new()

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
        for field, mint in (("input_mint", input_mint), ("output_mint", output_mint)):
            if self.is_settlement(mint):
                continue
            allowed = {asset.mint for asset in await self.load(tab) if asset.tradable}
            if mint not in allowed:
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
        if tab == "stocks":
            return (
                f"stocks:jupiter:{self.settings.jupiter_stock_mints}:{self.settings.jupiter_etf_mints}:"
                f"{self.settings.asset_registry_file or ''}"
            )
        source = self.settings.preipo_api_url
        return f"{tab}:{source or 'unconfigured'}:{self.settings.preipo_pinned_mints if tab == 'pre-ipo' else ''}"

    @staticmethod
    def _split_mints(value: str) -> list[str]:
        valid: list[str] = []
        for item in value.split(","):
            mint = item.strip()
            if not mint:
                continue
            try:
                require_solana_address(mint, field="mint")
            except AppError:
                continue
            if mint not in valid:
                valid.append(mint)
        return valid

    @staticmethod
    def _normalize_operator_mints(
        tokens: dict[str, dict[str, Any]],
        mints: list[str],
        kind: AssetKind,
        registry: dict[str, dict[str, str]],
    ) -> list[Asset]:
        assets: list[Asset] = []
        for mint in mints:
            row = tokens.get(mint)
            registry_row = registry.get(mint, {})
            # The operator registry is the source of admission. Jupiter is an
            # enrichment source and may not have indexed every issuer mint.
            symbol = (
                AssetAllowlist._text(row or {}, "symbol")
                or registry_row.get("ticker")
                or mint[:6].upper()
            )
            name = (
                AssetAllowlist._text(row or {}, "name")
                or registry_row.get("name")
                or symbol
            )
            logo_url = AssetAllowlist._text(row or {}, "icon", "logoURI", "logo_url", "logoUrl")
            decimals = (row or {}).get("decimals", 6)
            assets.append(
                Asset(
                    mint=mint,
                    symbol=symbol[:24],
                    name=name[:160],
                    kind=kind,
                    decimals=decimals if isinstance(decimals, int) and 0 <= decimals <= 18 else 6,
                    news_symbol=symbol[:12],
                    logo_url=logo_url,
                    verified=True,
                    tradable=True,
                )
            )
        return assets

    def _load_registry(self) -> dict[str, dict[str, str]]:
        path_value = self.settings.asset_registry_file
        if not path_value:
            return {}
        path = Path(path_value)
        if not path.is_absolute() and not path.exists():
            # Support both `cd apps/api` and starting the API from the
            # repository root (the two common local/Railway layouts).
            path = Path(__file__).resolve().parents[2] / path_value
        try:
            with path.open(newline="", encoding="utf-8-sig") as handle:
                rows = csv.DictReader(handle)
                registry: dict[str, dict[str, str]] = {}
                for row in rows:
                    category = (row.get("Category") or "").strip().casefold()
                    if "sunrise stock" not in category and "sunrise etf" not in category:
                        continue
                    mint = (row.get("Mint Address") or "").strip()
                    if not mint:
                        continue
                    try:
                        require_solana_address(mint, field="mint")
                    except AppError:
                        continue
                    registry[mint] = {
                        "ticker": (row.get("Ticker") or "").strip(),
                        "name": (row.get("Company / Product") or "").strip(),
                    }
                return registry
        except OSError:
            return {}

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
                    decimals=AssetAllowlist._decimals(row),
                    news_symbol=AssetAllowlist._text(row, "underlyingSymbol", "underlying_symbol", "ticker"),
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
                    kind=AssetKind.PREIPO,
                    decimals=AssetAllowlist._decimals(row),
                    logo_url=logo_url,
                    verified=True,
                    tradable=True,
                )
            )
            seen.add(mint)
        return assets

    @staticmethod
    def _decimals(row: dict[str, Any]) -> int:
        value = row.get("decimals", 6)
        return value if isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 18 else 6

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

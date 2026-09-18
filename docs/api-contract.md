# API contract

The web app calls FastAPI through `apps/web/lib/api.ts`. Responses use JSON and return `X-Request-ID`. Domain errors use:

```json
{
  "error": {
    "code": "unsupported_asset",
    "message": "The requested mint is not in the approved asset allowlist.",
    "details": {},
    "request_id": "..."
  }
}
```

## Public routes

- `GET /api/health`, `GET /api/health/live`, `GET /api/health/ready`
- `GET /api/assets?tab=stocks|pre-ipo|new&query=&limit=&cursor=` - cached operator-reviewed discovery lists
- `GET /api/assets/{mint}?tab=stocks|pre-ipo|new` - an asset resolved through the same allowlist
- `GET /api/market?symbols=` - live Finnhub quote feed; no synthetic fallback
- `GET /api/market/crypto?mints=` - live Jupiter crypto prices for the ticker feed
- `POST /api/quotes` - short-lived Jupiter quote with fee and signing fields; the API validates the selected allowlist first
- `GET /api/baskets`, `GET /api/baskets/{slug}` - public baskets
- `GET /api/gifts/{claim_code}` - gift claim status
- `GET /api/news?symbol=&days=` - cached Finnhub company and earnings news
- `GET /api/social/leaderboard?period=24h|7d`
- `GET /api/mcp/manifest` - machine-readable tool catalog

Provider-unavailable reads return an explicit `not_configured` state or an empty result with `configured: false`. The API never invents mints, balances, prices, or transaction signatures.

## Official asset allowlist

`app/lib/allowlist.py` is the only mint authority for the product:

- `stocks` loads the operator-provided `JUPITER_STOCK_MINTS` and `JUPITER_ETF_MINTS`. If `ASSET_REGISTRY_FILE` is configured, its ticker/name fields are used as a fallback; Jupiter Tokens metadata enriches the same mints when indexed.
- `pre-ipo` loads the optional PreStocks feed from `PREIPO_API_URL` and keeps only `PREIPO_PINNED_MINTS`.
- `new` loads the operator-owned launch index from `NEW_LAUNCHES_FILE`.
- Each source is cached for `ALLOWLIST_CACHE_SECONDS` (900 seconds by default).
- SOL, USDC, and USDT are settlement assets. They may be the non-stock side of a trade, but they are never valid stock/list entries.
- Stock-to-stock requests require both mints in the selected tab.
- Jupiter metadata does not decide eligibility; only the configured operator mint lists can admit stock or ETF assets.

## Wallet routes

Local development uses `X-Wallet-Address` only when `APP_ENV=development` and `AUTH_REQUIRED=false`. Production must replace this boundary with verified Privy token-to-wallet resolution.

- `GET /api/trades?limit=` and `GET /api/trades/{trade_id}`
- `POST /api/trades` with `Idempotency-Key`
- `POST /api/trades/{trade_id}/submit`
- `GET /api/orders?limit=`
- `POST /api/orders` with `Idempotency-Key` (Trigger V2 adapter; scheduled-order vault/auth flow remains a provider-specific integration boundary)
- `POST /api/orders/{order_id}/submit`
- `POST /api/baskets` with `tab` and `Idempotency-Key` where applicable
- `POST /api/gifts` with `tab` and `Idempotency-Key`
- `GET /api/portfolio`
- `GET /api/identity/me`, `PATCH /api/identity/me`
- `GET /api/watchlist`, `POST /api/watchlist/{mint}?tab=`, `DELETE /api/watchlist/{mint}`

## Trade and order rules

- Solana is the default rail.
- Base remains disabled unless explicitly enabled.
- Only allowlisted, verified, tradable mints may be traded, ordered, gifted, watched, or placed in a basket.
- Atomic amounts are positive integer strings.
- Quotes and executable instructions expire.
- The backend prepares and records intents; the connected wallet signs.
- A submitted signature is recorded for reconciliation. The API does not receive private keys.
- Trade, order, gift, and basket mutations use database constraints and idempotency keys where applicable.

## Database

Development may use `DB_AUTO_CREATE=true` with SQLite. Production must set `DB_AUTO_CREATE=false` and run:

```bash
uv run alembic upgrade head
```

The `0002_intent_tabs.py` migration stores the selected allowlist tab on trade and order intents.

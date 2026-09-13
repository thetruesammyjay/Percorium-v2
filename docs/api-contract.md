# API contract

The web app calls FastAPI through `apps/web/lib/api.ts`. All responses use JSON and return an `X-Request-ID` header. Domain errors use:

```json
{
  "error": {
    "code": "unsupported_asset",
    "message": "The requested asset is not supported.",
    "details": {},
    "request_id": "..."
  }
}
```

## Public routes

- `GET /api/health`, `GET /api/health/live`, `GET /api/health/ready`
- `GET /api/assets?query=&limit=&cursor=` â€” verified, tradable Sunrise assets
- `POST /api/quotes` â€” short-lived quote with fee and signing fields
- `GET /api/baskets` â€” public baskets
- `GET /api/gifts/{claim_code}` â€” gift claim status
- `GET /api/news?symbol=&days=` â€” cached Finnhub company and earnings news
- `GET /api/social/leaderboard?period=24h|7d`
- `GET /api/mcp/manifest` â€” machine-readable tool catalog

Provider-unavailable reads return an explicit `not_configured` state or an empty result with `configured: false`. The API never invents mints, balances, prices, or transaction signatures.

## Wallet routes

Local development uses `X-Wallet-Address` only when `APP_ENV=development` and `AUTH_REQUIRED=false`. Production must replace this boundary with verified Privy token-to-wallet resolution.

- `GET /api/trades?limit=` and `GET /api/trades/{trade_id}`
- `POST /api/trades` with `Idempotency-Key`
- `POST /api/trades/{trade_id}/submit`
- `GET /api/orders?limit=`
- `POST /api/orders` with `Idempotency-Key`
- `POST /api/orders/{order_id}/submit`
- `POST /api/baskets`
- `POST /api/gifts` with `Idempotency-Key`
- `GET /api/portfolio`
- `GET /api/identity/me`, `PATCH /api/identity/me`
- `GET /api/watchlist`, `POST /api/watchlist/{mint}`, `DELETE /api/watchlist/{mint}`

## Trade and order rules

- Solana is the default rail.
- Only official, verified, tradable Sunrise mints may be traded or ordered.
- SOL and the configured USDC mint are valid settlement assets.
- The Base rail returns `rail_disabled` until explicitly enabled.
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

The initial migration lives in `alembic/versions/0001_initial.py`.

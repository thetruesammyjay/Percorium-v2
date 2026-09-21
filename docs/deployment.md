# Deployment

Percorium deploys as two services:

- **Railway:** FastAPI from `apps/api`, connected to Neon PostgreSQL.
- **Vercel:** Next.js from `apps/web`, connected to the Railway API.

## Railway API

Create a Railway service from the repository and set its root directory to `apps/api`. The checked-in [`railway.json`](../apps/api/railway.json) selects the Dockerfile, runs the Alembic migration before deploy, and configures the health check and restart policy.

If Railway asks for commands, use:

```text
Build:  uv sync --frozen --no-dev
Start: uv run --no-dev uvicorn app.main:app --host 0.0.0.0 --port $PORT
Healthcheck: /api/health/live
```

Run the database migration as the Railway pre-deploy command:

```text
uv run --no-dev alembic upgrade head
```

Set these Railway variables in the **production** environment:

```text
APP_ENV=production
DATABASE_URL=<Neon pooled or direct PostgreSQL URL>
DB_AUTO_CREATE=false
AUTH_REQUIRED=true
CORS_ORIGINS=https://your-real-domain.com,https://www.your-real-domain.com
NEXT_PUBLIC_API_URL=<not set on Railway>
JUPITER_API_KEY=<Jupiter key>
JUPITER_STOCK_MINTS=<comma-separated real Solana stock mints>
JUPITER_ETF_MINTS=<comma-separated real Solana ETF mints>
ASSET_REGISTRY_FILE=<path to the reviewed registry CSV, if used>
ALCHEMY_SOLANA_RPC_URL=<mainnet RPC URL>
PRIVY_APP_ID=<Privy app id>
PRIVY_APP_SECRET=<Privy server secret>
PLATFORM_FEE_WALLET=<fee token account>
FINNHUB_API_KEY=<Finnhub key, if news is enabled>
```

`JUPITER_STOCK_MINTS` and `JUPITER_ETF_MINTS` must contain actual base58 Solana mint addresses. Values such as `mint1` or `mint4` are ignored. `ASSET_REGISTRY_FILE` is optional metadata for those operator-selected mints; Jupiter enriches it when the mint is indexed, but Jupiter's metadata search is not the source of admission.

If Railway uses `apps/api` as the service root, a CSV stored only at the repository root is outside the image build context. Copy the reviewed registry into `apps/api` (for example `apps/api/asset_registry.csv`) and set `ASSET_REGISTRY_FILE=asset_registry.csv`, or omit the registry and keep the operator mint lists in Railway variables.

After the first deploy, verify:

```text
https://<railway-domain>/api/health/live
https://<railway-domain>/api/health/ready
```

## Vercel web app

Create a Vercel project from the same repository and set **Root Directory** to `apps/web`. The checked-in [`vercel.json`](../apps/web/vercel.json) selects Next.js and uses the frozen pnpm lockfile during install.

Set these Vercel variables for Preview and Production as appropriate:

```text
NEXT_PUBLIC_API_URL=https://<railway-domain>/api
NEXT_PUBLIC_PRIVY_APP_ID=<Privy app id>
NEXT_PUBLIC_SOLANA_CLUSTER=mainnet-beta
```

Add the real domain in Vercel, then add that exact `https://` origin to Railway's `CORS_ORIGINS`. Add the `www` origin too if DNS will serve both forms.

## Local development

Keep local API settings separate from Railway:

```text
APP_ENV=development
DB_AUTO_CREATE=true
AUTH_REQUIRED=false
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

Local wallet-only routes use `X-Wallet-Address`. Do not carry that development bypass into the public deployment. The current API intentionally fails closed for production wallet routes until server-side Privy access-token verification is wired; implement that verifier before enabling real authenticated trading on Railway.

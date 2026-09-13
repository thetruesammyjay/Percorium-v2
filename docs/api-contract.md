# API contract

The web app calls FastAPI through `apps/web/lib/api.ts`. Domain routes are grouped by capability:

- `GET /api/health`
- `GET /api/assets?query=` — official Sunrise allowlist search
- `POST /api/quotes` — quote intent for a supported rail
- `POST /api/trades` — wallet-signature trade intent
- `GET /api/orders`, `/api/baskets`, `/api/portfolio`, `/api/news`
- `GET /api/gifts/{claim_id}` and `GET /api/identity/me`
- `GET /api/social/leaderboard`
- `GET /api/mcp/manifest`

The scaffold returns explicit `not_configured` states until provider credentials and persistence are connected. It must not invent asset mints or transaction signatures.

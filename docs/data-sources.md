# Data sources

- Operator registry: `sunrise_stocks_etfs_prestocks.csv` is a reviewed snapshot of stock, ETF, and Pre-IPO mint addresses. Configure it with `ASSET_REGISTRY_FILE`; the API admits only the configured stock/ETF mint lists and keeps the Pre-IPO rows separate.
- Jupiter Tokens API: metadata and artwork for the configured Solana mints; it is not the authority that decides whether a mint belongs in a shelf.
- PreStocks: optional Pre-IPO discovery source via `https://prestocks.com/api/prestocks`.
- Alchemy: Solana RPC and token-balance reads.
- Jupiter: prices, quotes, swaps, plus Trigger V2 limit/DCA boundaries, only after API allowlist validation.
- DexScreener: primary Solana pair charts; Gecko Terminal is the fallback.
- Finnhub: live market quotes and company/earnings news; links are cached and opened externally.
- Privy: Google authentication and Solana wallet onboarding.

Provider responses must be normalized and validated before they reach a signing flow. Provider availability is not proof that an asset or route is official.

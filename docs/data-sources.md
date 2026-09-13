# Data sources

- Sunrise: official stock and ETF mint allowlist, quotes, and execution.
- Alchemy: Solana RPC.
- Jupiter: swaps, Trigger V2 limit/DCA, and eligible lending discovery where supported.
- DexScreener: primary Solana pair charts; Gecko Terminal is the fallback.
- Finnhub: company and earnings news only; links are cached and opened externally.
- Privy: Google authentication and Solana wallet onboarding.

Every provider adapter should record source, fetched time, freshness, and the upstream identifier used for reconciliation.

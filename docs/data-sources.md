# Data sources

- Sunrise: official stock and ETF mint allowlist via `list-tokens`; it is not the execution engine.
- PreStocks: optional Pre-IPO discovery source via `https://prestocks.com/api/prestocks`.
- Alchemy: Solana RPC and token-balance reads.
- Jupiter: quotes and swaps, plus Trigger V2 limit/DCA boundaries, only after API allowlist validation.
- DexScreener: primary Solana pair charts; Gecko Terminal is the fallback.
- Finnhub: live market quotes and company/earnings news; links are cached and opened externally.
- Privy: Google authentication and Solana wallet onboarding.

Provider responses must be normalized and validated before they reach a signing flow. Provider availability is not proof that an asset or route is official.

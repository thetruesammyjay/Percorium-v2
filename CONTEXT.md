# Percorium project context

Percorium is being rebuilt as a Solana-first tokenized-stock aggregator. This repository is the new FastAPI + Next.js monorepo. The `Pundit/` directory is a legacy Base/EVM prototype kept only for reference and ignored by the new repository.

Current scaffold priorities:

1. Keep Sunrise-listed stock and ETF mints as the only supported asset universe.
2. Keep wallet signing and non-custodial boundaries explicit.
3. Keep provider-specific code behind FastAPI rail and integration adapters.
4. Keep Base hidden and disabled by default while Solana integration is implemented.
5. Treat the brand exports as replaceable assets, with semantic state colors separate from decorative green.

# Architecture

Percorium is a two-application monorepo. Next.js owns rendering and interaction. FastAPI owns domain validation, provider integrations, persistence, fee calculation, and transaction preparation.

The first rail is Solana: Sunrise is the official asset-list authority, Jupiter owns quote/swap and Trigger V2 boundaries, Alchemy is the RPC boundary, and the connected wallet signs. Base remains isolated behind a disabled-by-default adapter so it can be re-enabled from Settings without shaping the first-run experience.

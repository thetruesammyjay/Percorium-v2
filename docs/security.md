# Security boundaries

Wallets sign transactions. The API prepares and validates intents but must not custody private keys or silently submit user trades. Privy credentials and all provider secrets belong only in `apps/api/.env`.

Validate every asset against the official Sunrise mint allowlist. Validate SNS links against the resolved public key. Treat claim links, handles, transaction signatures, and wallet addresses as untrusted input. Keep MagicBlock off by default and expose Base only through an explicit Settings flag.

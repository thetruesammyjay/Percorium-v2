# Data dictionary

| Field | Meaning |
| --- | --- |
| `mint` | Solana public key for an official Sunrise-listed asset. |
| `symbol` | Display ticker supplied by the asset registry. |
| `kind` | `stock` or `etf`. |
| `rail` | `solana` by default; `base` only when explicitly enabled. |
| `fee_bps` | Platform fee in basis points; Percorium is configured for 50. |
| `wallet` | Public signing address; never a private key. |
| `tx_signature` | On-chain transaction identifier used for social callouts and reconciliation. |

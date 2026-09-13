# Data dictionary

| Field | Meaning |
| --- | --- |
| `mint` | Solana public key for an official Sunrise-listed asset. |
| `symbol` | Display ticker supplied by the asset registry. |
| `kind` | `stock` or `etf`. |
| `rail` | `solana` by default; `base` only when explicitly enabled and implemented. |
| `fee_bps` | Platform fee in basis points; Percorium is configured for 50. |
| `platform_fee` | Total fee charged to the trade input amount. |
| `copy_master_fee` | Ten percent of the platform fee for eligible copy-once trades. |
| `percorium_fee` | Platform fee retained by Percorium after the copy-master allocation. |
| `wallet` | Public signing address; never a private key. |
| `tx_signature` | On-chain transaction identifier used for social callouts and reconciliation. |
| `is_private` | Prevents the trade from appearing in public social aggregation. |
| `status` | Explicit lifecycle state such as awaiting signature, submitted, confirmed, failed, or expired. |

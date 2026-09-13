# Percorium Brand Asset Package

Production-oriented flat assets derived from the Percorium visual direction.

## Product identity

- `apps/web/public/brand/logo/percorium-mark.svg` — primary flat orbital P mark.
- `percorium-mark-mono.svg` — single-color mark using `currentColor`, ideal for dense product surfaces when inlined.
- `percorium-wordmark.svg` — font-independent outlined vector wordmark.
- `percorium-lockup-trade-smarter.svg` — flat marketing/onboarding lockup.
- `favicon.svg` — compact tab/app surface mark.

## Asset marks

`assets/generated/` contains custom ticker monograms rather than copied third-party company logos. The included AAPL/MSFT/etc. files are examples of the system, **not a claim that they are the canonical Sunrise universe**.

Populate `src/brand/sunrise-assets.ts` only with canonical Sunrise mint addresses supplied by the project or Sunrise metadata. The required mapping is:

`mint → ticker → name → asset type → mark`

Use `tools/generate_ticker_mark.py` to create more monograms.

## Semantic state rules

The semantic colors are intentionally separated from the decorative sticker palette:

- Success: `#147a51` / soft `#ddf6ea`
- Warning: `#9a6500` / soft `#fff1c2`
- Blocked: `#b42318` / soft `#ffe4e1`
- Pending: `#4f46b5` / soft `#e7e7ff`

Never rely on color alone. Pair each state with an icon, text label and, where useful, an explanation.

## Product vs marketing

Use the flat SVG system inside navigation, tables, trade flows, wallets, order states and small screens. Keep the 3D PNGs under `marketing/` for hero/onboarding/campaign usage only.

All production SVG assets use transparent bounds, solid fills and no gradients or raster shadows.

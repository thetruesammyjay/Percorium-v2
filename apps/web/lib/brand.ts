// The supplied export bundle currently lives under this preserved asset path.
// Keep the path in one place so it can be normalized later without touching UI code.
export const BRAND_ASSET_ROOT = "/brand/apps/web/public/brand";

export const brandAssets = {
  logo: {
    png: `${BRAND_ASSET_ROOT}/logo/Percorium.png`,
    bot: `${BRAND_ASSET_ROOT}/Percorium_bot.png`,
    mark: `${BRAND_ASSET_ROOT}/logo/percorium-mark.svg`,
    mono: `${BRAND_ASSET_ROOT}/logo/percorium-mark-mono.svg`,
    wordmark: `${BRAND_ASSET_ROOT}/logo/percorium-wordmark.svg`,
    lockup: `${BRAND_ASSET_ROOT}/logo/percorium-lockup-trade-smarter.svg`,
    favicon: `${BRAND_ASSET_ROOT}/logo/favicon.svg`,
  },
  categories: {
    stock: `${BRAND_ASSET_ROOT}/categories/stock.svg`,
    etf: `${BRAND_ASSET_ROOT}/categories/etf.svg`,
    sector: `${BRAND_ASSET_ROOT}/categories/sector.svg`,
    esg: `${BRAND_ASSET_ROOT}/categories/esg.svg`,
    topGainer: `${BRAND_ASSET_ROOT}/categories/top-gainer.svg`,
    topLoser: `${BRAND_ASSET_ROOT}/categories/top-loser.svg`,
  },
  states: {
    success: `${BRAND_ASSET_ROOT}/states/success.svg`,
    warning: `${BRAND_ASSET_ROOT}/states/warning.svg`,
    blocked: `${BRAND_ASSET_ROOT}/states/blocked.svg`,
    pending: `${BRAND_ASSET_ROOT}/states/pending.svg`,
  },
  ticker: (symbol: string) => `${BRAND_ASSET_ROOT}/assets/generated/${symbol.toUpperCase()}.svg`,
} as const;

export type BrandCategory = keyof typeof brandAssets.categories;
export const generatedTickerMarks = new Set(["AAPL", "AMZN", "ARKK", "MSFT", "NVDA", "QQQ", "SPY", "TSLA", "VOO", "VTI"]);
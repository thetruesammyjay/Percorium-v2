// Public brand files are served from /brand by Next.js.
export const BRAND_ASSET_ROOT = "/brand";

export const brandAssets = {
  logo: {
    png: `${BRAND_ASSET_ROOT}/Percorium-final-logo.png`,
    bot: `${BRAND_ASSET_ROOT}/Percorium-Mascot.png`,
    mark: `${BRAND_ASSET_ROOT}/apps/web/public/brand/logo/percorium-mark.svg`,
    mono: `${BRAND_ASSET_ROOT}/apps/web/public/brand/logo/percorium-mark-mono.svg`,
    wordmark: `${BRAND_ASSET_ROOT}/apps/web/public/brand/logo/percorium-wordmark.svg`,
    lockup: `${BRAND_ASSET_ROOT}/apps/web/public/brand/logo/percorium-lockup-trade-smarter.svg`,
    favicon: `${BRAND_ASSET_ROOT}/favicon.ico`,
  },
  categories: {
    stock: `${BRAND_ASSET_ROOT}/apps/web/public/brand/categories/stock.svg`,
    etf: `${BRAND_ASSET_ROOT}/apps/web/public/brand/categories/etf.svg`,
    sector: `${BRAND_ASSET_ROOT}/apps/web/public/brand/categories/sector.svg`,
    esg: `${BRAND_ASSET_ROOT}/apps/web/public/brand/categories/esg.svg`,
    topGainer: `${BRAND_ASSET_ROOT}/apps/web/public/brand/categories/top-gainer.svg`,
    topLoser: `${BRAND_ASSET_ROOT}/apps/web/public/brand/categories/top-loser.svg`,
  },
  states: {
    success: `${BRAND_ASSET_ROOT}/apps/web/public/brand/states/success.svg`,
    warning: `${BRAND_ASSET_ROOT}/apps/web/public/brand/states/warning.svg`,
    blocked: `${BRAND_ASSET_ROOT}/apps/web/public/brand/states/blocked.svg`,
    pending: `${BRAND_ASSET_ROOT}/apps/web/public/brand/states/pending.svg`,
  },
  ticker: (symbol: string) => `${BRAND_ASSET_ROOT}/apps/web/public/brand/assets/generated/${symbol.toUpperCase()}.svg`,
} as const;

export type BrandCategory = keyof typeof brandAssets.categories;
export const generatedTickerMarks = new Set(["AAPL", "AMZN", "ARKK", "MSFT", "NVDA", "QQQ", "SPY", "TSLA", "VOO", "VTI"]);

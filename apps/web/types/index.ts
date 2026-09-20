export type Rail = "solana" | "base";
export type AssetKind = "stock" | "etf" | "pre-ipo" | "memestock";
export type TradeMode = "swap" | "limit" | "dca";
export type DiscoveryTab = "stocks" | "pre-ipo";

export type Asset = {
  symbol: string;
  name: string;
  mint: string;
  kind: AssetKind;
  logo_url?: string;
  verified?: boolean;
  tradable?: boolean;
  news_symbol?: string | null;
};

export type AssetListResponse = {
  items: Asset[];
  source: string;
  configured: boolean;
  message?: string | null;
  next_cursor?: string | null;
  limit?: number;
};

export type MarketQuote = {
  symbol: string;
  mint?: string | null;
  logo_url?: string | null;
  price: number;
  change: number;
  change_percent: number;
  high?: number | null;
  low?: number | null;
  open?: number | null;
  previous_close?: number | null;
  as_of?: string | null;
  source: string;
};

export type MarketFeedResponse = {
  items: MarketQuote[];
  symbols: string[];
  configured: boolean;
  source: string;
  fetched_at: string;
  message?: string | null;
};

export type NewsItem = {
  id: string;
  symbol: string;
  headline: string;
  summary?: string | null;
  source: string;
  url: string;
  published_at: string;
  category: string;
};

export type NewsResponse = {
  items: NewsItem[];
  configured: boolean;
  fallback_symbol?: string | null;
  cached?: boolean;
  message?: string | null;
};

export type WatchlistItem = {
  mint: string;
  created_at: string;
};

export type WatchlistResponse = {
  items: WatchlistItem[];
};

export type QuoteRequest = {
  rail: "solana";
  tab: DiscoveryTab;
  sell_mint: string;
  buy_mint: string;
  sell_amount: string;
  slippage_bps: number;
  mode: "exact_in";
};

export type QuoteResponse = {
  status: "ready" | "not_configured";
  rail: Rail;
  tab: DiscoveryTab;
  sell_mint: string;
  buy_mint: string;
  sell_amount: string;
  expected_buy_amount?: string | null;
  price_impact_bps?: number | null;
  fee_bps: number;
  platform_fee: string;
  network_fee: string;
  total_debit: string;
  expires_at?: string | null;
  transaction?: string | null;
  signing_required: boolean;
  message?: string | null;
};

export type TradeCreateRequest = {
  rail: "solana";
  tab: DiscoveryTab;
  wallet: string;
  sell_mint: string;
  buy_mint: string;
  sell_amount: string;
  slippage_bps: number;
  order_type: "market";
  copy_master: boolean;
  is_private: boolean;
};

export type TradeResponse = Omit<QuoteResponse, "status"> & {
  status: "awaiting_signature" | "submitted" | "confirmed" | "failed" | "expired" | "not_configured";
  id?: string | null;
  tx_signature?: string | null;
};

export type OrderCreateRequest = {
  rail: "solana";
  tab: DiscoveryTab;
  wallet: string;
  input_mint: string;
  output_mint: string;
  amount: string;
  order_type: "limit" | "dca";
  limit_price?: string | null;
  interval_seconds?: number | null;
  occurrences?: number | null;
  slippage_bps: number;
};

export type OrderResponse = {
  id?: string | null;
  status: "awaiting_signature" | "submitted" | "active" | "filled" | "cancelled" | "failed" | "expired" | "not_configured";
  rail: Rail;
  tab: DiscoveryTab;
  wallet: string;
  order_type: "limit" | "dca";
  input_mint: string;
  output_mint: string;
  amount: string;
  limit_price?: string | null;
  interval_seconds?: number | null;
  occurrences?: number | null;
  fee_bps: number;
  platform_fee: string;
  total_debit: string;
  expires_at?: string | null;
  transaction?: string | null;
  provider_order_id?: string | null;
  tx_signature?: string | null;
  signing_required: boolean;
  message: string;
};

export type PortfolioToken = {
  mint: string;
  symbol: string;
  name: string;
  raw_amount: string;
  decimals: number;
  value_usd?: string | null;
};

export type PortfolioResponse = {
  status: "ready" | "not_configured";
  wallet: string;
  native_balance_lamports: string;
  tokens: PortfolioToken[];
  source: string;
  message?: string | null;
};

export type GiftCreateRequest = {
  tab: DiscoveryTab;
  sender_wallet: string;
  asset_mint: string;
  amount: string;
  recipient_reference: string;
};

export type GiftResponse = {
  claim_code: string;
  asset_mint: string;
  amount: string;
  recipient_reference: string;
  status: string;
  expires_at: string;
};

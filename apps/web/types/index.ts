export type Rail = "solana" | "base";
export type AssetKind = "stock" | "etf";

export type Asset = {
  symbol: string;
  name: string;
  mint: string;
  kind: AssetKind;
  logo_url?: string;
};

export type AssetListResponse = { items: Asset[]; source: string; configured: boolean };

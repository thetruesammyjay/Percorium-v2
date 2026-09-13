export function AssetMark({ symbol, kind }: { symbol: string; kind: "stock" | "etf" }) {
  return <span className="status status-pending" aria-label={`${kind} asset ${symbol}`}>{symbol}</span>;
}

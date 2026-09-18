export function AssetIcon({
  symbol,
  kind = "stock",
  size = 52,
  logoUrl,
}: {
  symbol?: string;
  kind?: "stock" | "etf";
  size?: number;
  logoUrl?: string | null;
}) {
  const normalizedSymbol = symbol?.toUpperCase();
  if (logoUrl) {
    // Provider artwork comes from Jupiter token metadata or Finnhub profiles;
    // avoid a growing Next image host allowlist.
    return <span className="asset-icon asset-icon-remote" style={{ width: size, height: size }}>
      {/* eslint-disable-next-line @next/next/no-img-element -- provider hosts return the artwork URL. */}
      <img src={logoUrl} alt="" width={size} height={size} />
    </span>;
  }
  const fallback = normalizedSymbol?.slice(0, 5) ?? (kind === "etf" ? "ETF" : "STK");
  return (
    <span
      className={`asset-icon asset-icon-fallback asset-icon-fallback-${kind}`}
      style={{ width: size, height: size }}
      aria-hidden="true"
    >
      {fallback}
    </span>
  );
}

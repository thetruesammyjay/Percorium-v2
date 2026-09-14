import Image from "next/image";

import { brandAssets, generatedTickerMarks } from "@/lib/brand";

export function AssetIcon({
  symbol,
  kind = "stock",
  size = 52,
}: {
  symbol?: string;
  kind?: "stock" | "etf";
  size?: number;
}) {
  const normalizedSymbol = symbol?.toUpperCase();
  const src = normalizedSymbol && generatedTickerMarks.has(normalizedSymbol)
    ? brandAssets.ticker(normalizedSymbol)
    : brandAssets.categories[kind];
  return <Image className="asset-icon" src={src} alt="" width={size} height={size} />;
}
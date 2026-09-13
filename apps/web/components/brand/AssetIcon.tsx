import Image from "next/image";

import { brandAssets } from "@/lib/brand";

export function AssetIcon({ symbol, kind = "stock", size = 52 }: { symbol?: string; kind?: "stock" | "etf"; size?: number }) {
  const src = symbol ? brandAssets.ticker(symbol) : brandAssets.categories[kind];
  return <Image className="asset-icon" src={src} alt="" width={size} height={size} />;
}

import Link from "next/link";

import { AssetIcon } from "@/components/brand/AssetIcon";
import { Badge } from "@/components/ui/Badge";
import { Arrow } from "@/components/ui/Arrow";

export function AssetRow({ symbol, name, kind, change = "—", href = "/assets" }: { symbol: string; name: string; kind: "stock" | "etf"; change?: string; href?: string }) {
  return <Link className="asset-row" href={href}><AssetIcon symbol={symbol} kind={kind} size={48} /><span className="asset-copy"><strong>{symbol}</strong><span>{name}</span></span><Badge tone={kind === "etf" ? "violet" : "blue"}>{kind.toUpperCase()}</Badge><span className="asset-change">{change}</span><Arrow /></Link>;
}

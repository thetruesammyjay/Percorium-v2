import Link from "next/link";

import { AssetIcon } from "@/components/brand/AssetIcon";
import { Badge } from "@/components/ui/Badge";
import { Arrow } from "@/components/ui/Arrow";
import type { AssetKind } from "@/types";

export function AssetRow({
  symbol,
  name,
  kind,
  logoUrl,
  change = "—",
  href = "/assets",
}: {
  symbol: string;
  name: string;
  kind: AssetKind;
  logoUrl?: string | null;
  change?: string;
  href?: string;
}) {
  return (
    <Link className="asset-row" href={href}>
      <AssetIcon symbol={symbol} kind={kind === "etf" ? "etf" : "stock"} logoUrl={logoUrl} size={48} />
      <span className="asset-copy"><strong>{symbol}</strong><span>{name}</span></span>
      <Badge tone={kind === "etf" ? "violet" : "blue"}>{kind.toUpperCase()}</Badge>
      <span className="asset-change">{change}</span>
      <Arrow />
    </Link>
  );
}

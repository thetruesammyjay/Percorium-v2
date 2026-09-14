import Image from "next/image";

import { DexScreenerChart } from "@/components/charts/DexScreenerChart";
import { brandAssets } from "@/lib/brand";
import { apiErrorMessage, getAsset } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { SectionLabel } from "@/components/ui/SectionLabel";
import { StatusPill } from "@/components/ui/StatusPill";
import type { DiscoveryTab } from "@/types";

export default async function AssetPage({
  params,
  searchParams,
}: {
  params: Promise<{ mint: string }>;
  searchParams?: Promise<{ tab?: string }>;
}) {
  const { mint } = await params;
  const query = searchParams ? await searchParams : {};
  const tab: DiscoveryTab | undefined = query.tab === "pre-ipo" ? "pre-ipo" : query.tab === "stocks" ? "stocks" : undefined;
  let asset = null;
  let error = "The official asset registry is unavailable.";
  try {
    asset = await getAsset(mint, tab);
  } catch (requestError) {
    error = apiErrorMessage(requestError);
  }

  return <section className="band band-sky"><div className="page-shell"><div className="page-hero"><div><SectionLabel>{asset ? `${asset.kind === "etf" ? "ETF" : "Stock"} asset` : "Asset lookup"}</SectionLabel><h1>{asset?.symbol ?? "Asset"}</h1></div><div><StatusPill status={asset ? "success" : "warning"}>{asset ? "Official asset" : "Unavailable"}</StatusPill><p>{asset ? asset.name : error}</p></div></div>{asset ? <div className="ticket-layout"><div className="product-card product-card-white"><Image src={asset.kind === "etf" ? brandAssets.categories.etf : brandAssets.categories.stock} alt="Asset category" width={72} height={72} /><h3>{asset.name}</h3><p>Canonical mint<br /><code>{asset.mint}</code></p><Button href={`/trade?buy=${encodeURIComponent(asset.mint)}`}>Trade this asset →</Button></div><div className="product-card product-card-gray chart-card"><SectionLabel>Live chart · DexScreener</SectionLabel><DexScreenerChart mint={asset.mint} symbol={asset.symbol} /></div></div> : <div className="empty-state"><h3>We could not verify that mint.</h3><p>Open Discover and choose an asset from the official {tab === "pre-ipo" ? "Pre-IPO" : "Stocks"} list.</p><Button href={`/assets${tab ? `?tab=${tab}` : ""}`}>Back to Discover</Button></div>}</div></section>;
}
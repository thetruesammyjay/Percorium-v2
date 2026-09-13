import Image from "next/image";

import { brandAssets } from "@/lib/brand";
import { Button } from "@/components/ui/Button";
import { SectionLabel } from "@/components/ui/SectionLabel";
import { StatusPill } from "@/components/ui/StatusPill";

export default async function AssetPage({ params }: { params: Promise<{ mint: string }> }) {
  const { mint } = await params;
  return <><section className="band band-sky"><div className="page-shell"><div className="page-hero"><div><SectionLabel>Sunrise asset</SectionLabel><h1>{mint}</h1></div><div><StatusPill status="success">Registry route</StatusPill><p>Asset detail is keyed by the canonical Sunrise mint.</p></div></div><div className="ticket-layout"><div className="product-card product-card-white"><Image src={brandAssets.categories.stock} alt="Asset category" width={72} height={72} /><h3>Metadata ready for sync.</h3><p>Company details, price, market status, and earnings news will populate from the official registry and Finnhub cache.</p><Button href="/trade">Trade this asset →</Button></div><div className="product-card product-card-gray"><SectionLabel>Chart surface</SectionLabel><div className="empty-state"><p>DexScreener pair chart<br />Gecko fallback</p></div></div></div></div></section></>;
}
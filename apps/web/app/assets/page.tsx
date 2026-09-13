import Image from "next/image";
import Link from "next/link";

import { brandAssets } from "@/lib/brand";
import { AssetRow } from "@/components/market/AssetRow";
import { SectionLabel } from "@/components/ui/SectionLabel";
import { StatusPill } from "@/components/ui/StatusPill";

const assets = [["AAPL", "Apple Inc.", "stock", "+2.41%"], ["AMZN", "Amazon.com, Inc.", "stock", "+1.86%"], ["NVDA", "NVIDIA Corporation", "stock", "+4.18%"], ["QQQ", "Nasdaq 100", "etf", "+1.07%"], ["SPY", "S&P 500", "etf", "+0.62%"], ["VTI", "Total US Market", "etf", "+0.48%"]] as const;

export default function AssetsPage() {
  return <><section className="band band-gray"><div className="page-shell"><div className="page-hero"><div><SectionLabel>Sunrise registry</SectionLabel><h1>Find your<br />signal.</h1></div><div><StatusPill status="success">Verified list</StatusPill><p>Only official Sunrise-listed mints are eligible for Percorium trading.</p></div></div><div className="product-card product-card-white"><label className="field">Search the market<input placeholder="Ticker, company, or category" /></label><div className="asset-list">{assets.slice(0, 3).map(([symbol, name, kind, change]) => <AssetRow key={symbol} symbol={symbol} name={name} kind={kind} change={change} href={`/assets/${symbol}`} />)}</div></div></div></section><section className="band band-white"><div className="page-shell"><div className="section-heading"><div><SectionLabel>Browse the list</SectionLabel><h2>Recognizable<br />marks.</h2></div><Image src={brandAssets.categories.stock} alt="Stock category" width={72} height={72} /></div><div className="asset-list">{assets.slice(3).map(([symbol, name, kind, change]) => <AssetRow key={symbol} symbol={symbol} name={name} kind={kind} change={change} href={`/assets/${symbol}`} />)}</div><Link className="button button-secondary page-section" href="/baskets">See preset ETFs →</Link></div></section></>;
}
import Image from "next/image";
import Link from "next/link";

import { brandAssets } from "@/lib/brand";
import { Button } from "@/components/ui/Button";
import { SectionLabel } from "@/components/ui/SectionLabel";

const basketModes = [
  { title: "Preset ETFs", copy: "Start with a official index or ETF mint.", icon: brandAssets.categories.etf, href: "/assets", tone: "panel-white", action: "Browse ETFs" },
  { title: "Custom basket", copy: "Choose 2–8 official mints and keep the weights honest.", icon: brandAssets.categories.sector, href: "/trade", tone: "panel-yellow", action: "Choose assets" },
  { title: "Share the thought", copy: "A public link opens a preview. It never trades silently.", icon: brandAssets.categories.esg, href: "/b/your-idea", tone: "panel-lavender", action: "Preview a share" },
] as const;

export default function BasketsPage() {
  return <><section className="band band-violet"><div className="page-shell"><div className="page-hero"><div><SectionLabel>Compose your view</SectionLabel><h1>Ideas with<br />weight.</h1></div><div><p>Build a basket from 2–8 official mints. Balance the weights to 100%, then share the idea at /b.</p><Button href="/trade" variant="secondary">Trade an asset →</Button></div></div><div className="card-grid">{basketModes.map((mode) => <article className={`sticker-panel ${mode.tone}`} key={mode.title}><Image className="panel-icon" src={mode.icon} alt="" width={56} height={56} /><h3>{mode.title}</h3><p>{mode.copy}</p><Link className="button button-secondary" href={mode.href}>{mode.action} →</Link></article>)}</div></div></section><section className="band band-white"><div className="page-shell"><div className="section-heading"><div><SectionLabel>Your baskets</SectionLabel><h2>Nothing saved.<br />Yet.</h2></div><p>Saved baskets will keep their assets, weights, and share link together in one quiet place.</p></div><div className="empty-state"><h3>Start with a clear idea.</h3><p>Choose a preset or compose a basket from the verified official list. Persistence will be connected to your wallet profile.</p><Button href="/assets">Find official assets →</Button></div></div></section></>;
}
import Link from "next/link";

import { Button } from "@/components/ui/Button";
import { SectionLabel } from "@/components/ui/SectionLabel";
import { StatusPill } from "@/components/ui/StatusPill";

export default function DashboardPage() {
  return (
    <>
      <section className="band band-mint"><div className="page-shell"><div className="page-hero"><div><SectionLabel>Your command center</SectionLabel><h1>Good morning,<br />let&apos;s orbit.</h1></div><div><StatusPill status="pending">Wallet not connected</StatusPill><p>Connect a wallet to make the dashboard yours.</p><Button href="/trade">Connect &amp; trade</Button></div></div><div className="card-grid"><Link className="sticker-panel panel-white" href="/portfolio"><SectionLabel>Portfolio value</SectionLabel><h3>-</h3><p>Balances appear after your first signed position.</p></Link><Link className="sticker-panel panel-yellow" href="/watchlist"><SectionLabel>Watchlist</SectionLabel><h3>Keep signal close</h3><p>Save a ticker from Discover to keep its chart and news nearby.</p></Link><article className="sticker-panel panel-violet"><SectionLabel>Social pulse</SectionLabel><h3>Fresh canvas</h3><p>Public fills, private by default.</p></article></div></div></section>
      <section className="band band-white"><div className="page-shell"><div className="section-heading"><div><SectionLabel>Keep moving</SectionLabel><h2>What&apos;s next?</h2></div><p>A small dashboard with a short path to the things you can control.</p></div><div className="ticket-layout"><Link className="product-card product-card-white" href="/assets"><SectionLabel>01 · Discover</SectionLabel><h3>Find an official asset</h3><p>Search official stock and ETF mints, then open a focused detail page.</p><span className="arrow">-&gt;</span></Link><Link className="product-card product-card-white" href="/baskets"><SectionLabel>02 · Compose</SectionLabel><h3>Build a basket</h3><p>Bring 2-8 official mints to a 100% weighted, shareable idea.</p><span className="arrow">-&gt;</span></Link></div></div></section>
    </>
  );
}

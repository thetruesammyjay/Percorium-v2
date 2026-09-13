import Image from "next/image";

import { brandAssets } from "@/lib/brand";
import { SectionLabel } from "@/components/ui/SectionLabel";
import { StatusPill } from "@/components/ui/StatusPill";

export default function LeaderboardPage() {
  return <section className="band band-gray"><div className="page-shell"><div className="page-hero"><div><SectionLabel>Public fills · private by default</SectionLabel><h1>See who’s<br />moving.</h1></div><div><StatusPill status="success">24h · 7d</StatusPill><p>Leaderboard rankings use Percorium fills. Private trades stay private.</p></div></div><div className="ticket-layout"><div className="empty-state"><Image src={brandAssets.categories.topGainer} alt="Top gainer" width={64} height={64} /><h3>The board is clear.</h3><p>Once signed trades are indexed, top fills and copy-once entries will show up here.</p></div><article className="product-card product-card-white"><SectionLabel>Callouts</SectionLabel><h3>Share a signal, not a sermon.</h3><p>Up to 140 characters. One official mint. One transaction. No auto-bots.</p><StatusPill status="warning">No public fills yet</StatusPill></article></div></div></section>;
}
import { Button } from "@/components/ui/Button";
import { SectionLabel } from "@/components/ui/SectionLabel";
import { StatusPill } from "@/components/ui/StatusPill";

export default async function SharedBasketPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <section className="band band-lavender"><div className="page-shell"><div className="page-hero"><div><SectionLabel>Shared basket · /b/{id}</SectionLabel><h1>See the<br />weight.</h1></div><div><StatusPill status="pending">Preview only</StatusPill><p>Public links explain an idea. They never trade silently.</p></div></div><div className="empty-state"><h3>Basket data is not connected yet.</h3><p>This public route is ready for a 2–8 mint basket with 100% weights.</p><Button href="/baskets">Build your own →</Button></div></div></section>;
}
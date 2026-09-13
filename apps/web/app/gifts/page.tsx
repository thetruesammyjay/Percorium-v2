import Image from "next/image";

import { brandAssets } from "@/lib/brand";
import { Button } from "@/components/ui/Button";
import { SectionLabel } from "@/components/ui/SectionLabel";

export default function GiftsPage() {
  return <section className="band band-yellow"><div className="page-shell"><div className="page-hero"><div><SectionLabel>Send something with a claim</SectionLabel><h1>Give an<br />orbit.</h1></div><div><p>Make a Jupiter-style claim link for an official stock or ETF. The recipient signs up, creates a wallet, and claims.</p><Button href="/trade">Start with an asset →</Button></div></div><div className="ticket-layout"><section className="product-card product-card-white"><Image src={brandAssets.categories.stock} alt="Stock gift" width={64} height={64} /><h3>Gift flow</h3><div className="field-grid"><label className="field">Asset<select defaultValue="Choose an asset"><option>Choose an asset</option><option>AAPL · Apple</option><option>QQQ · Nasdaq 100</option></select></label><label className="field">Amount<input placeholder="0.00" inputMode="decimal" /></label></div><label className="field">Recipient<input placeholder="@handle, .sol, or .sns" /></label><Button>Create claim link</Button></section><aside className="product-card product-card-gray"><SectionLabel>For the recipient</SectionLabel><h3>One link. New wallet.</h3><p>Privy signup and wallet creation happen at claim time. Name resolution must match the recipient’s public key.</p></aside></div></div></section>;
}
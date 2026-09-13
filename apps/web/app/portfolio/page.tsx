import { Button } from "@/components/ui/Button";
import { SectionLabel } from "@/components/ui/SectionLabel";
import { StatusPill } from "@/components/ui/StatusPill";

export default function PortfolioPage() {
  return <section className="band band-mint"><div className="page-shell"><div className="page-hero"><div><SectionLabel>Wallet view</SectionLabel><h1>What you<br />hold.</h1></div><div><StatusPill status="pending">No wallet connected</StatusPill><p>Connect a wallet to read balances and signed activity.</p><Button href="/trade">Connect wallet</Button></div></div><div className="card-grid"><article className="sticker-panel panel-white"><SectionLabel>Total value</SectionLabel><h3>—</h3><p>Value follows the wallet, not a spreadsheet.</p></article><article className="sticker-panel panel-blue"><SectionLabel>Positions</SectionLabel><h3>0 assets</h3><p>Official Sunrise positions appear after your first fill.</p></article><article className="sticker-panel panel-yellow"><SectionLabel>Fee rate</SectionLabel><h3>50 bps</h3><p>Shown before signing each Percorium trade.</p></article></div></div></section>;
}
import { Button } from "@/components/ui/Button";
import { SectionLabel } from "@/components/ui/SectionLabel";
import { StatusPill } from "@/components/ui/StatusPill";

export default async function GiftClaimPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <section className="band band-yellow"><div className="page-shell"><div className="page-hero"><div><SectionLabel>Gift claim · /g/{id}</SectionLabel><h1>Your gift<br />is waiting.</h1></div><div><StatusPill status="success">Claim link found</StatusPill><p>Sign up with Privy, create a wallet, and claim the asset.</p></div></div><div className="product-card product-card-white"><h3>Connect or create a wallet</h3><p>The claim flow will verify the link and deliver the signed transfer to your wallet.</p><Button>Continue with Google →</Button></div></div></section>;
}
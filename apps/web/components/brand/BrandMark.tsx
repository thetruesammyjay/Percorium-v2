import Image from "next/image";

import { brandAssets } from "@/lib/brand";

type BrandMarkProps = { compact?: boolean };

export function BrandMark({ compact = false }: BrandMarkProps) {
  return <span className={`brand-lockup${compact ? " brand-lockup-compact" : ""}`}><Image className="brand-logo-image" src={brandAssets.logo.png} alt="Percorium" width={92} height={78} priority /><span className="brand-sr-only">Percorium</span></span>;
}
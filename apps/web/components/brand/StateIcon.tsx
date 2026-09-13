import Image from "next/image";

import { brandAssets } from "@/lib/brand";

export function StateIcon({ state, size = 24 }: { state: "success" | "warning" | "blocked" | "pending"; size?: number }) {
  return <Image src={brandAssets.states[state]} alt="" width={size} height={size} />;
}

"use client";

import { useEffect, useState } from "react";

import { getAssets } from "@/lib/api";
import type { Asset } from "@/types";

export function useAssets(query?: string) {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setLoading(true);
    getAssets(query).then((items) => { if (active) setAssets(items); }).catch(() => { if (active) setAssets([]); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [query]);

  return { assets, loading };
}

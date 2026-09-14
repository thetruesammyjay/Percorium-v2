"use client";

import { useEffect, useState } from "react";

import { AssetRow } from "@/components/market/AssetRow";
import { apiErrorMessage, getMarketFeed } from "@/lib/api";
import type { MarketFeedResponse } from "@/types";

export function LiveMarketPreview() {
  const [feed, setFeed] = useState<MarketFeedResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const response = await getMarketFeed();
        if (active) {
          setFeed(response);
          setError(null);
        }
      } catch (requestError) {
        if (active) setError(apiErrorMessage(requestError));
      }
    };
    void load();
    const interval = window.setInterval(load, 30_000);
    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, []);

  if (!feed?.items.length) {
    return <div className="empty-state"><p>{error ?? feed?.message ?? "Connect Finnhub to show live market quotes."}</p></div>;
  }

  return <div className="asset-list">
    {feed.items.slice(0, 4).map((quote) => (
      <AssetRow
        key={quote.symbol}
        symbol={quote.symbol}
        name="Market quote"
        kind="stock"
        change={(quote.change_percent >= 0 ? "+" : "") + quote.change_percent.toFixed(2) + "%"}
        href={`/assets?query=${encodeURIComponent(quote.symbol)}`}
      />
    ))}
  </div>;
}
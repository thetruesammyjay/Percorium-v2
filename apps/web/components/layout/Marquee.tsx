"use client";

import { useEffect, useState } from "react";

import { AssetIcon } from "@/components/brand/AssetIcon";
import { apiErrorMessage, getCryptoMarketFeed } from "@/lib/api";
import type { MarketQuote } from "@/types";

function formatPrice(value: number) {
  if (value >= 1000) return "$" + value.toLocaleString("en-US", { maximumFractionDigits: 0 });
  if (value >= 1) return "$" + value.toLocaleString("en-US", { maximumFractionDigits: 2 });
  return "$" + value.toLocaleString("en-US", { maximumFractionDigits: 6 });
}

function CryptoTicker({ quote }: { quote: MarketQuote }) {
  const positive = quote.change_percent >= 0;
  return (
    <span className="marquee-item">
      <AssetIcon symbol={quote.symbol} kind="stock" logoUrl={quote.logo_url} size={22} />
      <strong>{quote.symbol}</strong>
      <span>{formatPrice(quote.price)}</span>
      <span className={positive ? "marquee-positive" : "marquee-negative"}>
        {positive ? "+" : ""}{quote.change_percent.toFixed(2)}%
      </span>
    </span>
  );
}

export function Marquee() {
  const [quotes, setQuotes] = useState<MarketQuote[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const response = await getCryptoMarketFeed();
        if (active) {
          setQuotes(response.items);
          setError(response.message ?? null);
        }
      } catch (requestError) {
        if (active) setError(apiErrorMessage(requestError));
      }
    };
    void load();
    const interval = window.setInterval(() => void load(), 30_000);
    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, []);

  const visibleQuotes = quotes.length ? quotes : [];
  return (
    <div className="marquee" aria-label="Live crypto market feed" aria-live="polite">
      <div className="marquee-track">
        {visibleQuotes.length ? (
          [...visibleQuotes, ...visibleQuotes].map((quote, index) => <CryptoTicker key={`${quote.mint ?? quote.symbol}-${index}`} quote={quote} />)
        ) : (
          <span className="marquee-item"><strong>LIVE CRYPTO FEED</strong><span>{error ?? "Connecting to Jupiter prices"}</span></span>
        )}
      </div>
    </div>
  );
}

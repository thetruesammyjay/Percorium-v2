"use client";

import { useEffect, useState } from "react";

const DEXSCREENER_API = "https://api.dexscreener.com/token-pairs/v1/solana/";
const DEXSCREENER_APP = "https://dexscreener.com/solana/";

type Pair = {
  pairAddress?: string;
  quoteToken?: { symbol?: string };
  liquidity?: { usd?: number | null } | null;
};

type Props = {
  mint: string;
  symbol: string;
};

function choosePair(pairs: Pair[]): string | null {
  return [...pairs]
    .filter((pair) => typeof pair.pairAddress === "string" && pair.pairAddress.length > 0)
    .sort((left, right) => {
      const leftStable = /^(USDC|USDT)$/i.test(left.quoteToken?.symbol ?? "") ? 1 : 0;
      const rightStable = /^(USDC|USDT)$/i.test(right.quoteToken?.symbol ?? "") ? 1 : 0;

      if (leftStable !== rightStable) {
        return rightStable - leftStable;
      }

      return (right.liquidity?.usd ?? 0) - (left.liquidity?.usd ?? 0);
    })[0]?.pairAddress ?? null;
}

export function DexScreenerChart({ mint, symbol }: Props) {
  const [pairAddress, setPairAddress] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [unavailable, setUnavailable] = useState(false);

  useEffect(() => {
    let active = true;

    setLoading(true);
    setUnavailable(false);
    setPairAddress(null);

    fetch(DEXSCREENER_API + encodeURIComponent(mint), {
      headers: { Accept: "application/json" },
    })
      .then(async (response) => {
        if (!response.ok) {
          throw new Error("DexScreener pair lookup failed");
        }

        return response.json() as Promise<Pair[]>;
      })
      .then((pairs) => {
        if (!active) {
          return;
        }

        const selectedPair = choosePair(Array.isArray(pairs) ? pairs : []);
        setPairAddress(selectedPair);
        setUnavailable(!selectedPair);
      })
      .catch(() => {
        if (active) {
          setUnavailable(true);
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false);
        }
      });

    return () => {
      active = false;
    };
  }, [mint]);

  if (loading) {
    return (
      <div className="chart-loading" role="status">
        <span />
        Loading live chart...
      </div>
    );
  }

  if (unavailable || !pairAddress) {
    return (
      <div className="chart-unavailable">
        <p>No liquid market is available for {symbol} yet.</p>
        <a
          href={DEXSCREENER_APP + encodeURIComponent(mint)}
          target="_blank"
          rel="noreferrer"
        >
          Open DexScreener -&gt;
        </a>
      </div>
    );
  }

  const embedUrl = DEXSCREENER_APP + encodeURIComponent(pairAddress) + "?embed=1&theme=light&trades=0&info=0";

  return (
    <div className="chart-embed">
      <iframe
        title={symbol + " live market chart"}
        src={embedUrl}
        loading="lazy"
        allow="clipboard-write"
        referrerPolicy="strict-origin-when-cross-origin"
      />
    </div>
  );
}

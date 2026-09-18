"use client";

import { useEffect, useState } from "react";

import { useWallet } from "@/components/providers/Providers";
import { addToWatchlist, apiErrorMessage, getWatchlist, removeFromWatchlist } from "@/lib/api";
import type { DiscoveryTab } from "@/types";

export function WatchlistButton({ mint, tab = "stocks" }: { mint: string; tab?: DiscoveryTab }) {
  const wallet = useWallet();
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    if (!wallet.connected || !wallet.address) {
      setSaved(false);
      return () => {
        active = false;
      };
    }
    void getWatchlist(wallet.address).then((response) => {
      if (active) setSaved(response.items.some((item) => item.mint === mint));
    }).catch(() => {
      if (active) setMessage("Connect your wallet again to load your watchlist.");
    });
    return () => {
      active = false;
    };
  }, [mint, wallet.address, wallet.connected]);

  async function toggle() {
    if (!wallet.connected || !wallet.address) {
      setMessage("Connect your wallet to save assets.");
      return;
    }
    setBusy(true);
    setMessage(null);
    try {
      if (saved) {
        await removeFromWatchlist(mint, wallet.address);
        setSaved(false);
      } else {
        await addToWatchlist(mint, wallet.address, tab);
        setSaved(true);
      }
    } catch (error) {
      setMessage(apiErrorMessage(error));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="watchlist-control">
      <button className="button button-secondary" type="button" onClick={toggle} disabled={busy} aria-pressed={saved}>
        {busy ? "Saving..." : saved ? "Remove from watchlist" : "Add to watchlist"}
      </button>
      {message && <p className="field-note">{message}</p>}
    </div>
  );
}

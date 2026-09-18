"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { AssetIcon } from "@/components/brand/AssetIcon";
import { useWallet } from "@/components/providers/Providers";
import { Button } from "@/components/ui/Button";
import { SectionLabel } from "@/components/ui/SectionLabel";
import { StatusPill } from "@/components/ui/StatusPill";
import { apiErrorMessage, getAssets, getWatchlist, removeFromWatchlist } from "@/lib/api";
import type { Asset, WatchlistItem } from "@/types";

export default function WatchlistPage() {
  const wallet = useWallet();
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [assets, setAssets] = useState<Asset[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let active = true;
    if (!wallet.connected || !wallet.address) {
      setItems([]);
      setAssets([]);
      setError(null);
      return () => {
        active = false;
      };
    }
    setLoading(true);
    void Promise.all([getWatchlist(wallet.address), getAssets(undefined, "stocks"), getAssets(undefined, "pre-ipo").catch(() => [])])
      .then(([watchlist, stocks, preIpo]) => {
        if (!active) return;
        setItems(watchlist.items);
        setAssets([...stocks, ...preIpo]);
        setError(null);
      })
      .catch((requestError) => {
        if (active) setError(apiErrorMessage(requestError));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [wallet.address, wallet.connected]);

  const assetByMint = useMemo(() => new Map(assets.map((asset) => [asset.mint, asset])), [assets]);

  async function remove(mint: string) {
    if (!wallet.address) return;
    try {
      await removeFromWatchlist(mint, wallet.address);
      setItems((current) => current.filter((item) => item.mint !== mint));
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    }
  }

  const connected = Boolean(wallet.connected && wallet.address);

  return (
    <section className="band band-lavender">
      <div className="page-shell">
        <div className="page-hero">
          <div><SectionLabel>Personal signal</SectionLabel><h1>Keep it<br />close.</h1></div>
          <div><StatusPill status={connected ? "success" : "pending"}>{connected ? "Wallet watchlist" : "Wallet not connected"}</StatusPill><p>Save official assets and return to their chart, news, and trade ticket quickly.</p></div>
        </div>
        {!connected ? (
          <div className="empty-state"><h3>Connect a wallet to see your watchlist.</h3><p>Watchlists are stored per wallet and stay separate from the public market feed.</p><Button href="/trade">Connect wallet</Button></div>
        ) : loading ? (
          <div className="empty-state"><p>Loading your watchlist...</p></div>
        ) : error ? (
          <div className="empty-state"><StatusPill status="warning">Watchlist unavailable</StatusPill><p>{error}</p></div>
        ) : items.length === 0 ? (
          <div className="empty-state"><h3>Your watchlist is empty.</h3><p>Open an official asset and save it when you want it nearby.</p><Button href="/assets">Discover assets</Button></div>
        ) : (
          <div className="asset-list watchlist-list">
            {items.map((item) => {
              const asset = assetByMint.get(item.mint);
              return (
                <div className="watchlist-row" key={item.mint}>
                  <Link className="watchlist-asset" href={`/assets/${item.mint}${asset?.kind === "pre-ipo" ? "?tab=pre-ipo" : ""}`}>
                    <AssetIcon symbol={asset?.symbol ?? item.mint.slice(0, 6)} kind={asset?.kind === "etf" ? "etf" : "stock"} logoUrl={asset?.logo_url} size={48} />
                    <span className="asset-copy"><strong>{asset?.symbol ?? "Unknown mint"}</strong><span>{asset?.name ?? item.mint}</span></span>
                  </Link>
                  <button className="text-link watchlist-remove" type="button" onClick={() => void remove(item.mint)}>Remove</button>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </section>
  );
}

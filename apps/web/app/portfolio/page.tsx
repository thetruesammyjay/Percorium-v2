"use client";

import { useEffect, useState } from "react";

import { useWallet } from "@/components/providers/Providers";
import { Button } from "@/components/ui/Button";
import { SectionLabel } from "@/components/ui/SectionLabel";
import { StatusPill } from "@/components/ui/StatusPill";
import { apiErrorMessage, getPortfolio } from "@/lib/api";
import { formatAtomicAmount, shortenAddress } from "@/lib/utils";
import type { PortfolioResponse } from "@/types";

export default function PortfolioPage() {
  const wallet = useWallet();
  const [portfolio, setPortfolio] = useState<PortfolioResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!wallet.address || !wallet.connected) {
      setPortfolio(null);
      return;
    }
    let active = true;
    const load = async () => {
      try {
        const response = await getPortfolio(wallet.address!);
        if (active) {
          setPortfolio(response);
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
  }, [wallet.address, wallet.connected]);

  const connected = Boolean(wallet.address && wallet.connected);
  const status = error ? "warning" : connected && portfolio?.status === "ready" ? "success" : "pending";
  const statusText = error ? "Portfolio unavailable" : connected ? portfolio?.status === "ready" ? "Live wallet" : "Portfolio waiting" : "No wallet connected";

  return <section className="band band-mint"><div className="page-shell"><div className="page-hero"><div><SectionLabel>Wallet view</SectionLabel><h1>What you<br />hold.</h1></div><div><StatusPill status={status}>{statusText}</StatusPill><p>{error ?? (connected ? `Reading ${shortenAddress(wallet.address!)}` : "Connect a wallet to read balances and signed activity.")}</p>{!connected && <Button href="/trade">Connect wallet</Button>}</div></div><div className="card-grid"><article className="sticker-panel panel-white"><SectionLabel>Native balance</SectionLabel><h3>{portfolio ? formatAtomicAmount(portfolio.native_balance_lamports, 9) + " SOL" : "—"}</h3><p>Read from the connected Solana wallet through Alchemy.</p></article><article className="sticker-panel panel-blue"><SectionLabel>Official positions</SectionLabel><h3>{portfolio ? `${portfolio.tokens.length} asset${portfolio.tokens.length === 1 ? "" : "s"}` : "—"}</h3><p>Only mints present in the active official allowlists are shown.</p></article><article className="sticker-panel panel-yellow"><SectionLabel>Fee rate</SectionLabel><h3>50 bps</h3><p>Shown before signing each Percorium trade.</p></article></div>{connected && portfolio?.tokens.length ? <div className="page-section"><div className="section-heading"><div><SectionLabel>Balances</SectionLabel><h2>Keep it<br />visible.</h2></div><p>Token amounts are raw on-chain balances formatted with each mint’s decimals.</p></div><div className="asset-list">{portfolio.tokens.map((token) => <div className="asset-row" key={token.mint}><span className="asset-copy"><strong>{token.symbol}</strong><span>{token.name}</span></span><span className="asset-change">{formatAtomicAmount(token.raw_amount, token.decimals)}</span><span /></div>)}</div></div> : connected && <div className="page-section"><div className="empty-state"><h3>No official positions yet.</h3><p>{portfolio?.message ?? "Your connected wallet has no balances in the approved asset set."}</p><Button href="/assets">Discover assets</Button></div></div>}</div></section>;
}
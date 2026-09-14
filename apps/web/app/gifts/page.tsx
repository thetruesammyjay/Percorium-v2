"use client";

import Image from "next/image";
import { useEffect, useState } from "react";

import { AssetIcon } from "@/components/brand/AssetIcon";
import { useWallet } from "@/components/providers/Providers";
import { Button } from "@/components/ui/Button";
import { SectionLabel } from "@/components/ui/SectionLabel";
import { StatusPill } from "@/components/ui/StatusPill";
import { apiErrorMessage, createGift, getAssets } from "@/lib/api";
import { brandAssets } from "@/lib/brand";
import { toAtomicAmount } from "@/lib/utils";
import type { Asset, GiftResponse } from "@/types";

export default function GiftsPage() {
  const wallet = useWallet();
  const [assets, setAssets] = useState<Asset[]>([]);
  const [assetMint, setAssetMint] = useState("");
  const [amount, setAmount] = useState("");
  const [recipient, setRecipient] = useState("");
  const [loadingAssets, setLoadingAssets] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<GiftResponse | null>(null);

  useEffect(() => {
    let active = true;
    getAssets(undefined, "stocks")
      .then((items) => {
        if (!active) return;
        setAssets(items);
        if (items[0]) setAssetMint(items[0].mint);
      })
      .catch((requestError) => {
        if (active) setError(apiErrorMessage(requestError));
      })
      .finally(() => {
        if (active) setLoadingAssets(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const submit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setResult(null);
    if (!wallet.connected || !wallet.address) {
      setError("Connect a Solana wallet before creating a claim link.");
      return;
    }
    if (!assetMint) {
      setError("Choose an approved Sunrise asset.");
      return;
    }
    const atomicAmount = toAtomicAmount(amount, 6);
    if (!atomicAmount) {
      setError("Enter an amount greater than zero with up to six decimal places.");
      return;
    }
    if (!recipient.trim()) {
      setError("Enter an @handle, .sol, or .sns recipient.");
      return;
    }
    setLoading(true);
    try {
      setResult(await createGift({
        tab: "stocks",
        sender_wallet: wallet.address,
        asset_mint: assetMint,
        amount: atomicAmount,
        recipient_reference: recipient.trim(),
      }));
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  };

  const selectedAsset = assets.find((asset) => asset.mint === assetMint);

  return <section className="band band-yellow"><div className="page-shell"><div className="page-hero"><div><SectionLabel>Send something with a claim</SectionLabel><h1>Give an<br />orbit.</h1></div><div><StatusPill status={wallet.connected ? "success" : "pending"}>{wallet.connected ? "Wallet ready" : "Wallet required"}</StatusPill><p>Create a claim intent for an official Sunrise stock or ETF. The recipient signs up, creates a wallet, and claims.</p></div></div><div className="ticket-layout"><form className="product-card product-card-white" onSubmit={submit}><div className="gift-asset-heading">{selectedAsset ? <AssetIcon symbol={selectedAsset.symbol} kind={selectedAsset.kind} size={64} /> : <Image src={brandAssets.categories.stock} alt="Stock gift" width={64} height={64} />}<div><SectionLabel>Official asset</SectionLabel><h3>Gift flow</h3></div></div><div className="field-grid"><label className="field">Asset<select value={assetMint} onChange={(event) => setAssetMint(event.target.value)} disabled={loadingAssets || !assets.length}><option value="">{loadingAssets ? "Loading approved assets…" : "Choose an approved asset"}</option>{assets.map((asset) => <option key={asset.mint} value={asset.mint}>{asset.symbol} · {asset.name}</option>)}</select></label><label className="field">Amount<input value={amount} onChange={(event) => setAmount(event.target.value)} placeholder="0.00" inputMode="decimal" /></label></div><label className="field">Recipient<input value={recipient} onChange={(event) => setRecipient(event.target.value)} placeholder="@handle, .sol, or .sns" /></label>{error && <p className="form-error" role="alert">{error}</p>}{result && <div className="action-result"><StatusPill status="success">Claim created</StatusPill><p>Share this link with the recipient:</p><code>/g/{result.claim_code}</code><p className="field-note">The claim is pending until its underlying transfer is funded.</p></div>}<button className="button button-primary" type="submit" disabled={loading || loadingAssets || !assets.length}>{loading ? "Creating…" : "Create claim link"}</button></form><aside className="product-card product-card-gray"><SectionLabel>For the recipient</SectionLabel><h3>One link. New wallet.</h3><p>Only mints from the official Stocks allowlist can be gifted. Name resolution must match the recipient’s public key before a transfer is released.</p><Button href="/assets">Browse official assets →</Button></aside></div></div></section>;
}

"use client";

import Image from "next/image";
import { useEffect, useMemo, useState } from "react";

import { brandAssets } from "@/lib/brand";
import {
  apiErrorMessage,
  createOrder,
  createQuote,
  createTrade,
  getAssets,
  submitOrder,
  submitTrade,
} from "@/lib/api";
import { PLATFORM_FEE_BPS, SOLANA_USDC_MINT, SOLANA_USDT_MINT, SOLANA_WRAPPED_SOL_MINT } from "@/lib/constants";
import { decodeBase64, encodeBase58, formatAtomicAmount, toAtomicAmount } from "@/lib/utils";
import { useWallet } from "@/components/providers/Providers";
import type { Asset, OrderResponse, QuoteResponse, TradeMode, TradeResponse } from "@/types";
import { SectionLabel } from "@/components/ui/SectionLabel";
import { StatusPill } from "@/components/ui/StatusPill";

type TradeAsset = {
  mint: string;
  symbol: string;
  name: string;
  kind: "stock" | "etf";
  decimals: number;
};

type ActionResponse = QuoteResponse | TradeResponse | OrderResponse;

const settlementAssets: TradeAsset[] = [
  { mint: SOLANA_USDC_MINT, symbol: "USDC", name: "USD Coin", kind: "etf", decimals: 6 },
  { mint: SOLANA_WRAPPED_SOL_MINT, symbol: "SOL", name: "Solana", kind: "stock", decimals: 9 },
  { mint: SOLANA_USDT_MINT, symbol: "USDT", name: "Tether USD", kind: "stock", decimals: 6 },
];

function statusForAction(action: ActionResponse | null): "success" | "warning" | "blocked" | "pending" {
  if (!action) return "pending";
  if (action.status === "ready" || action.status === "confirmed" || action.status === "filled") return "success";
  if (action.status === "not_configured" || action.status === "failed" || action.status === "expired") return "warning";
  return "pending";
}

function actionLabel(action: ActionResponse | null) {
  if (!action) return null;
  if (action.status === "not_configured") return "Provider setup required";
  if (action.status === "awaiting_signature") return "Signature required";
  if (action.status === "submitted") return "Submitted to Solana";
  if (action.status === "confirmed" || action.status === "filled") return "Complete";
  return action.status.replace("_", " ");
}

function formatInterval(minutes: string) {
  const value = Number(minutes);
  return Number.isFinite(value) && value > 0 ? value * 60 : null;
}

export default function TradePage() {
  const wallet = useWallet();
  const [mode, setMode] = useState<TradeMode>("swap");
  const [assets, setAssets] = useState<Asset[]>([]);
  const [assetsMessage, setAssetsMessage] = useState<string | null>(null);
  const [sellMint, setSellMint] = useState(SOLANA_USDC_MINT);
  const [buyMint, setBuyMint] = useState("");
  const [amount, setAmount] = useState("");
  const [slippageBps, setSlippageBps] = useState("100");
  const [limitPrice, setLimitPrice] = useState("");
  const [intervalMinutes, setIntervalMinutes] = useState("60");
  const [occurrences, setOccurrences] = useState("12");
  const [quote, setQuote] = useState<QuoteResponse | null>(null);
  const [action, setAction] = useState<ActionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [assetsLoading, setAssetsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    getAssets()
      .then((items) => {
        if (!active) return;
        setAssets(items);
        if (items[0]) setBuyMint(items[0].mint);
      })
      .catch((requestError) => {
        if (active) setAssetsMessage(apiErrorMessage(requestError));
      })
      .finally(() => {
        if (active) setAssetsLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const tradeAssets = useMemo<TradeAsset[]>(
    () => [...settlementAssets, ...assets.map((asset) => ({ ...asset, kind: asset.kind === "etf" ? "etf" as const : "stock" as const, decimals: 6 }))],
    [assets],
  );
  const sellAsset = tradeAssets.find((asset) => asset.mint === sellMint);
  const outputAssets = tradeAssets.filter((asset) => asset.mint !== sellMint);
  const buyAsset = tradeAssets.find((asset) => asset.mint === buyMint);
  const atomicAmount = sellAsset ? toAtomicAmount(amount, sellAsset.decimals) : null;
  const primaryLabel = loading
    ? "Preparing…"
    : mode === "swap"
      ? quote ? "Prepare signed swap" : "Review quote"
      : mode === "limit"
        ? "Create limit order"
        : "Create DCA order";

  const resetAction = () => {
    setQuote(null);
    setAction(null);
    setError(null);
  };

  const selectMode = (nextMode: TradeMode) => {
    setMode(nextMode);
    resetAction();
  };

  const selectSell = (mint: string) => {
    setSellMint(mint);
    if (mint === buyMint) setBuyMint(outputAssets.find((asset) => asset.mint !== mint)?.mint ?? "");
    resetAction();
  };

  const handlePrimary = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    if (!sellAsset || !buyAsset) {
      setError("Choose two different assets from the configured registry.");
      return;
    }
    if (!atomicAmount) {
      setError("Enter an amount greater than zero with valid decimal precision.");
      return;
    }

    setLoading(true);
    try {
      if (mode === "swap" && !quote) {
        const nextQuote = await createQuote({
          rail: "solana",
          tab: "stocks",
          sell_mint: sellMint,
          buy_mint: buyMint,
          sell_amount: atomicAmount,
          slippage_bps: Number(slippageBps) || 100,
          mode: "exact_in",
        });
        setQuote(nextQuote);
        setAction(nextQuote);
        return;
      }

      if (!wallet.connected || !wallet.address) {
        setError("Connect a Solana wallet before preparing a signed action.");
        return;
      }

      if (mode === "swap") {
        const trade = await createTrade({
          rail: "solana",
          tab: "stocks",
          wallet: wallet.address,
          sell_mint: sellMint,
          buy_mint: buyMint,
          sell_amount: atomicAmount,
          slippage_bps: Number(slippageBps) || 100,
          order_type: "market",
          copy_master: false,
          is_private: false,
        });
        setAction(trade);
        if (trade.id && trade.transaction && wallet.signAndSend) {
          const signatureBytes = await wallet.signAndSend(decodeBase64(trade.transaction));
          const submitted = await submitTrade(trade.id, wallet.address, encodeBase58(signatureBytes));
          setAction(submitted);
        }
        return;
      }

      const interval = mode === "dca" ? formatInterval(intervalMinutes) : null;
      if (mode === "dca" && !interval) {
        setError("Enter a DCA interval of at least one minute.");
        return;
      }
      if (mode === "limit" && (!limitPrice || Number(limitPrice) <= 0)) {
        setError("Enter a positive limit price.");
        return;
      }

      const order = await createOrder({
        rail: "solana",
        tab: "stocks",
        wallet: wallet.address,
        input_mint: sellMint,
        output_mint: buyMint,
        amount: atomicAmount,
        order_type: mode,
        limit_price: mode === "limit" ? limitPrice : null,
        interval_seconds: interval,
        occurrences: mode === "dca" ? Number(occurrences) || 1 : null,
        slippage_bps: Number(slippageBps) || 100,
      });
      setAction(order);
      if (order.id && order.transaction && wallet.signAndSend) {
        const signatureBytes = await wallet.signAndSend(decodeBase64(order.transaction));
        const submitted = await submitOrder(order.id, wallet.address, encodeBase58(signatureBytes));
        setAction(submitted);
      }
    } catch (requestError) {
      setError(apiErrorMessage(requestError));
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="band band-sky">
      <div className="page-shell">
        <div className="page-hero">
          <div><SectionLabel>Jupiter · Solana</SectionLabel><h1>Trade<br />with intent.</h1></div>
          <div>
            <StatusPill status={wallet.connected ? "success" : wallet.setupRequired ? "warning" : "pending"}>
              {wallet.connected ? "Wallet ready" : wallet.setupRequired ? "Wallet setup required" : "Awaiting wallet"}
            </StatusPill>
            <p>Your wallet signs. Percorium prepares. No private key touches the API.</p>
          </div>
        </div>
        <div className="ticket-layout">
          <form className="product-card product-card-white" onSubmit={handlePrimary}>
            <div className="trade-tabs" role="tablist" aria-label="Trade mode">
              {(["swap", "limit", "dca"] as const).map((tab) => (
                <button
                  className={"trade-tab" + (mode === tab ? " active" : "")}
                  type="button"
                  role="tab"
                  aria-selected={mode === tab}
                  key={tab}
                  onClick={() => selectMode(tab)}
                >
                  {tab === "dca" ? "DCA" : tab[0].toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>
            <div className="field-grid">
              <label className="field">You pay
                <select value={sellMint} onChange={(event) => selectSell(event.target.value)}>
                  {tradeAssets.map((asset) => <option key={asset.mint} value={asset.mint}>{asset.symbol} · {asset.name}</option>)}
                </select>
              </label>
              <label className="field">You receive
                <select value={buyMint} onChange={(event) => { setBuyMint(event.target.value); resetAction(); }} disabled={!outputAssets.length}>
                  <option value="">Choose an approved asset</option>
                  {outputAssets.map((asset) => <option key={asset.mint} value={asset.mint}>{asset.symbol} · {asset.name}</option>)}
                </select>
              </label>
            </div>
            <label className="field">Amount
              <input value={amount} onChange={(event) => { setAmount(event.target.value); resetAction(); }} placeholder="0.00" inputMode="decimal" />
            </label>
            {mode === "limit" && (
              <label className="field">Limit price in USD
                <input value={limitPrice} onChange={(event) => { setLimitPrice(event.target.value); resetAction(); }} placeholder="Target price" inputMode="decimal" />
              </label>
            )}
            {mode === "dca" && (
              <div className="field-grid">
                <label className="field">Every (minutes)
                  <input value={intervalMinutes} onChange={(event) => { setIntervalMinutes(event.target.value); resetAction(); }} min="1" type="number" />
                </label>
                <label className="field">Occurrences
                  <input value={occurrences} onChange={(event) => { setOccurrences(event.target.value); resetAction(); }} min="1" type="number" />
                </label>
              </div>
            )}
            <label className="field">Slippage tolerance (bps)
              <input value={slippageBps} onChange={(event) => { setSlippageBps(event.target.value); resetAction(); }} min="1" max="5000" type="number" />
            </label>
            <div className="fee-line"><span>Route</span><strong>Allowlist → Jupiter → Solana</strong></div>
            <div className="fee-line"><span>Platform fee</span><strong>{PLATFORM_FEE_BPS} bps</strong></div>
            {error && <p className="form-error" role="alert">{error}</p>}
            {assetsLoading && <p className="field-note">Loading approved stock assets…</p>}
            {!assetsLoading && !assets.length && <p className="field-note">{assetsMessage ?? "Approved stock assets are unavailable until the asset registry is configured."}</p>}
            <button className="button button-primary" type="submit" disabled={loading || !buyAsset}>
              {primaryLabel}
            </button>
            {action && (
              <div className="action-result">
                <StatusPill status={statusForAction(action)}>{actionLabel(action)}</StatusPill>
                <p>{action.message ?? "The request has been received."}</p>
                {action.status === "ready" && "expected_buy_amount" in action && action.expected_buy_amount && (
                  <div className="fee-line"><span>Expected receive</span><strong>{formatAtomicAmount(action.expected_buy_amount, buyAsset?.decimals ?? 6)} {buyAsset?.symbol}</strong></div>
                )}
              </div>
            )}
          </form>
          <aside className="product-card product-card-gray">
            <SectionLabel>Before you sign</SectionLabel>
            <Image src={brandAssets.states.pending} alt="Pending transaction" width={64} height={64} />
            <h3>Review every move.</h3>
            <p>Quotes, slippage, fees, and provider status stay visible before the wallet prompt. Nothing moves without your approval.</p>
            <StatusPill status={action ? statusForAction(action) : wallet.connected ? "success" : "pending"}>
              {action ? actionLabel(action) : wallet.connected ? "Wallet connected" : "No wallet connected"}
            </StatusPill>
          </aside>
        </div>
        <div className="card-grid page-section">
          <article className="sticker-panel panel-blue"><SectionLabel>Market</SectionLabel><h3>Stock → stock</h3><p>Only assets approved for the active discovery tab can reach Jupiter.</p></article>
          <article className="sticker-panel panel-lavender"><SectionLabel>Scheduled</SectionLabel><h3>DCA, on your terms</h3><p>Jupiter Trigger V2 prepares scheduled orders after its credentials are configured.</p></article>
          <article className="sticker-panel panel-yellow"><SectionLabel>Private</SectionLabel><h3>Quiet fills</h3><p>Private trade preferences are sent to the signed trade boundary.</p></article>
        </div>
      </div>
    </section>
  );
}

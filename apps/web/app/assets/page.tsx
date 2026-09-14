"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import { AssetIcon } from "@/components/brand/AssetIcon";
import { AssetRow } from "@/components/market/AssetRow";
import { apiErrorMessage, getAssetsPage, getMarketFeed } from "@/lib/api";
import { brandAssets } from "@/lib/brand";
import type { Asset, DiscoveryTab, MarketFeedResponse, MarketQuote } from "@/types";
import { Badge } from "@/components/ui/Badge";
import { SectionLabel } from "@/components/ui/SectionLabel";
import { StatusPill } from "@/components/ui/StatusPill";

type DiscoveryView = DiscoveryTab | "new";

function formatPrice(price: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(price);
}

function formatChange(value: number) {
  return (value >= 0 ? "+" : "") + value.toFixed(2) + "%";
}

function LiveQuoteCard({ quote }: { quote: MarketQuote }) {
  const positive = quote.change_percent >= 0;
  return (
    <article className="quote-card">
      <div className="quote-card-top">
        <AssetIcon symbol={quote.symbol} kind="stock" size={44} />
        <Badge tone={positive ? "mint" : "violet"}>{quote.symbol}</Badge>
      </div>
      <div className="quote-card-price">{formatPrice(quote.price)}</div>
      <div className={positive ? "quote-change quote-positive" : "quote-change quote-negative"}>
        {formatChange(quote.change_percent)} <span>today</span>
      </div>
    </article>
  );
}

function MarketFeed({ feed, loading, error }: { feed: MarketFeedResponse | null; loading: boolean; error: string | null }) {
  return (
    <section className="feed-section" aria-labelledby="live-feed-heading">
      <div className="feed-heading">
        <div>
          <SectionLabel>Live market feed</SectionLabel>
          <h2 id="live-feed-heading">Read the<br />room.</h2>
        </div>
        <div className="feed-meta">
          <StatusPill status={feed?.configured ? "success" : "pending"}>
            {feed?.configured ? "Finnhub live" : "Feed waiting"}
          </StatusPill>
          <p>Refreshes every 30 seconds. Quotes are market data, not asset eligibility.</p>
        </div>
      </div>
      {loading && !feed ? (
        <div className="empty-state"><p>Loading the latest market quotes…</p></div>
      ) : error ? (
        <div className="empty-state"><StatusPill status="warning">Feed unavailable</StatusPill><p>{error}</p></div>
      ) : feed?.items.length ? (
        <div className="quote-grid">{feed.items.map((quote) => <LiveQuoteCard key={quote.symbol} quote={quote} />)}</div>
      ) : (
        <div className="empty-state">
          <StatusPill status="pending">Finnhub not connected</StatusPill>
          <h3>Live prices will appear here.</h3>
          <p>{feed?.message ?? "Add FINNHUB_API_KEY to the API environment to start the feed."}</p>
        </div>
      )}
    </section>
  );
}

export default function AssetsPage() {
  const [view, setView] = useState<DiscoveryView>("stocks");
  const [query, setQuery] = useState("");
  const [assets, setAssets] = useState<Asset[]>([]);
  const [assetsConfigured, setAssetsConfigured] = useState(false);
  const [assetsMessage, setAssetsMessage] = useState<string | null>(null);
  const [assetsLoading, setAssetsLoading] = useState(true);
  const [assetsError, setAssetsError] = useState<string | null>(null);
  const [feed, setFeed] = useState<MarketFeedResponse | null>(null);
  const [feedLoading, setFeedLoading] = useState(true);
  const [feedError, setFeedError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    const loadFeed = async () => {
      try {
        const result = await getMarketFeed();
        if (active) {
          setFeed(result);
          setFeedError(null);
        }
      } catch (error) {
        if (active) setFeedError(apiErrorMessage(error));
      } finally {
        if (active) setFeedLoading(false);
      }
    };
    void loadFeed();
    const interval = window.setInterval(() => void loadFeed(), 30_000);
    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, []);

  useEffect(() => {
    let active = true;
    if (view === "new") {
      setAssets([]);
      setAssetsConfigured(false);
      setAssetsMessage("New discovery is curated separately and is not a tradable allowlist yet.");
      setAssetsLoading(false);
      setAssetsError(null);
      return () => {
        active = false;
      };
    }

    const timer = window.setTimeout(async () => {
      setAssetsLoading(true);
      try {
        const result = await getAssetsPage(query.trim() || undefined, view);
        if (active) {
          setAssets(result.items);
          setAssetsConfigured(result.configured);
          setAssetsMessage(result.message ?? null);
          setAssetsError(null);
        }
      } catch (error) {
        if (active) {
          setAssets([]);
          setAssetsError(apiErrorMessage(error));
        }
      } finally {
        if (active) setAssetsLoading(false);
      }
    }, 240);
    return () => {
      active = false;
      window.clearTimeout(timer);
    };
  }, [query, view]);

  const changeBySymbol = useMemo(
    () => new Map((feed?.items ?? []).map((quote) => [quote.symbol, formatChange(quote.change_percent)])),
    [feed],
  );

  const changeView = (nextView: DiscoveryView) => {
    setView(nextView);
    setQuery("");
  };

  return (
    <>
      <section className="band band-gray">
        <div className="page-shell">
          <div className="page-hero">
            <div><SectionLabel>Discover · Solana</SectionLabel><h1>Find your<br />signal.</h1></div>
            <div>
              <StatusPill status={assetsConfigured ? "success" : "pending"}>
                {assetsConfigured ? "Approved list" : "Source waiting"}
              </StatusPill>
              <p>Stocks are official. Pre-IPO is an optional PreStocks source. Jupiter token search is not used for discovery.</p>
            </div>
          </div>
          <div className="discovery-tabs" role="tablist" aria-label="Discovery source">
            {(["stocks", "pre-ipo", "new"] as const).map((tab) => (
              <button
                className={"discovery-tab" + (view === tab ? " active" : "")}
                type="button"
                role="tab"
                aria-selected={view === tab}
                key={tab}
                onClick={() => changeView(tab)}
              >
                {tab === "pre-ipo" ? "Pre-IPO" : tab[0].toUpperCase() + tab.slice(1)}
              </button>
            ))}
          </div>
          <div className="product-card product-card-white">
            <label className="field">Search approved assets
              <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder={view === "new" ? "New discovery is coming soon" : "Ticker, company, or category"} disabled={view === "new"} />
            </label>
            {assetsLoading ? (
              <div className="empty-state"><p>Loading the approved {view === "pre-ipo" ? "Pre-IPO" : "stock"} list…</p></div>
            ) : assetsError ? (
              <div className="empty-state"><StatusPill status="warning">Registry unavailable</StatusPill><p>{assetsError}</p></div>
            ) : assets.length ? (
              <div className="asset-list">{assets.map((asset) => (
                <AssetRow
                  key={asset.mint}
                  symbol={asset.symbol}
                  name={asset.name}
                  kind={asset.kind}
                  change={changeBySymbol.get(asset.symbol)}
                  href={"/assets/" + asset.mint}
                />
              ))}</div>
            ) : (
              <div className="empty-state">
                <StatusPill status={view === "new" ? "pending" : "warning"}>
                  {view === "new" ? "Not launched" : "Allowlist unavailable"}
                </StatusPill>
                <h3>{view === "new" ? "New assets need a source." : "No approved assets loaded."}</h3>
                <p>{assetsMessage ?? "Configure the source before displaying or trading any mint."}</p>
              </div>
            )}
          </div>
        </div>
      </section>
      <section className="band band-white">
        <div className="page-shell">
          <MarketFeed feed={feed} loading={feedLoading} error={feedError} />
          <div className="section-heading page-section">
            <div><SectionLabel>Source boundaries</SectionLabel><h2>Clear lists.<br />Quiet risk.</h2></div>
            <Image src={brandAssets.categories.stock} alt="Stock category" width={72} height={72} />
          </div>
          <Link className="button button-secondary" href="/trade">Open the trade ticket →</Link>
        </div>
      </section>
    </>
  );
}
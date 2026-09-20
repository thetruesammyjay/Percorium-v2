"use client";

import { useEffect, useState } from "react";

import { AssetIcon } from "@/components/brand/AssetIcon";
import { apiErrorMessage, getNewsFeed } from "@/lib/api";
import type { NewsItem } from "@/types";

function relativeDate(value: string): string {
  const timestamp = new Date(value).getTime();
  if (!Number.isFinite(timestamp)) return "Recently";
  const difference = timestamp - Date.now();
  const days = Math.round(Math.abs(difference) / 86_400_000);
  if (days === 0) return difference >= 0 ? "Today" : "Today";
  return difference > 0 ? `In ${days} day${days === 1 ? "" : "s"}` : `${days} day${days === 1 ? "" : "s"} ago`;
}

function categoryLabel(category: string): string {
  if (category === "ipo") return "IPO";
  if (category === "earnings") return "Earnings";
  return "Market";
}

function StoryRow({ item }: { item: NewsItem }) {
  return (
    <a className="new-feed-item" href={item.url} target="_blank" rel="noreferrer">
      <AssetIcon symbol={item.symbol === "MARKET" ? "NEWS" : item.symbol} kind="stock" size={36} />
      <span className="new-feed-item-copy">
        <span className="new-feed-item-meta">
          <span className="new-feed-category">{categoryLabel(item.category)}</span>
          <span>{relativeDate(item.published_at)}</span>
          <span>{item.source}</span>
        </span>
        <strong>{item.headline}</strong>
        {item.summary && <span className="new-feed-summary">{item.summary}</span>}
      </span>
    </a>
  );
}

export function TopStoriesFeed() {
  const [items, setItems] = useState<NewsItem[]>([]);
  const [configured, setConfigured] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const response = await getNewsFeed(7);
        if (!active) return;
        setItems(response.items);
        setConfigured(response.configured);
        setMessage(response.message ?? null);
      } catch (error) {
        if (active) setMessage(apiErrorMessage(error));
      } finally {
        if (active) setLoading(false);
      }
    };
    void load();
    const interval = window.setInterval(() => void load(), 300_000);
    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, []);

  return (
    <section className="new-feed-card" aria-labelledby="top-stories-heading">
      <div className="new-feed-heading">
        <div>
          <p className="eyebrow">Market intelligence</p>
          <h2 id="top-stories-heading">Top stories</h2>
        </div>
        <p>IPO listings, earnings reports, and technology stories that can move the market.</p>
      </div>
      {loading ? (
        <div className="new-feed-state">Loading the latest stories...</div>
      ) : !configured ? (
        <div className="new-feed-state">{message ?? "Add FINNHUB_API_KEY to load the New feed."}</div>
      ) : items.length ? (
        <div className="new-feed-list">{items.map((item) => <StoryRow item={item} key={item.id} />)}</div>
      ) : (
        <div className="new-feed-state">{message ?? "No new stories are available right now."}</div>
      )}
    </section>
  );
}

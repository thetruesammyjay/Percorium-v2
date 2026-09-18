"use client";

import { useEffect, useState } from "react";

import { apiErrorMessage, getNews } from "@/lib/api";
import type { NewsItem } from "@/types";

function publishedLabel(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Recently";
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric" }).format(date);
}

export function NewsFeed({ symbol }: { symbol: string }) {
  const [items, setItems] = useState<NewsItem[]>([]);
  const [configured, setConfigured] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;
    setLoading(true);
    void getNews(symbol, 7)
      .then((response) => {
        if (!active) return;
        setItems(response.items);
        setConfigured(response.configured);
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
  }, [symbol]);

  return (
    <section className="news-feed" aria-labelledby="news-heading">
      <div className="section-heading news-heading">
        <div>
          <p className="section-label">Finnhub · {symbol}</p>
          <h2 id="news-heading">What moved<br />the ticker.</h2>
        </div>
        <p>Company news and earnings headlines for the underlying listed symbol.</p>
      </div>
      {loading ? (
        <div className="news-state">Loading recent headlines...</div>
      ) : error ? (
        <div className="news-state">News is unavailable right now. {error}</div>
      ) : !configured ? (
        <div className="news-state">Add FINNHUB_API_KEY to show recent company news.</div>
      ) : items.length === 0 ? (
        <div className="news-state">No recent headlines for {symbol}.</div>
      ) : (
        <div className="news-list">
          {items.slice(0, 8).map((item) => (
            <a className="news-item" href={item.url} target="_blank" rel="noreferrer" key={item.id}>
              <span className="news-item-meta">{item.source} · {publishedLabel(item.published_at)}</span>
              <strong>{item.headline}</strong>
              {item.summary && <span>{item.summary}</span>}
            </a>
          ))}
        </div>
      )}
    </section>
  );
}

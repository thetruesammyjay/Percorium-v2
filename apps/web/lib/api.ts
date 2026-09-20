import { API_URL } from "@/lib/constants";
import type {
  Asset,
  AssetListResponse,
  DiscoveryTab,
  GiftCreateRequest,
  GiftResponse,
  MarketFeedResponse,
  NewsResponse,
  OrderCreateRequest,
  OrderResponse,
  PortfolioResponse,
  QuoteRequest,
  QuoteResponse,
  TradeCreateRequest,
  TradeResponse,
  WatchlistResponse,
} from "@/types";

export class ApiError extends Error {
  constructor(public readonly status: number, message: string) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(API_URL + path, {
    ...init,
    headers: { "Content-Type": "application/json", ...init?.headers },
  });
  if (!response.ok) throw new ApiError(response.status, await response.text());
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export async function getAssetsPage(query?: string, tab: DiscoveryTab = "stocks"): Promise<AssetListResponse> {
  const params = new URLSearchParams({ tab });
  if (query) params.set("query", query);
  return request<AssetListResponse>("/assets?" + params.toString(), { cache: "no-store" });
}

export async function getAsset(mint: string, tab?: DiscoveryTab): Promise<Asset> {
  const suffix = tab ? "?tab=" + encodeURIComponent(tab) : "";
  return request<Asset>("/assets/" + encodeURIComponent(mint) + suffix, { cache: "no-store" });
}

export async function getAssets(query?: string, tab: DiscoveryTab = "stocks"): Promise<Asset[]> {
  return (await getAssetsPage(query, tab)).items;
}

export async function getMarketFeed(symbols?: string[]): Promise<MarketFeedResponse> {
  const suffix = symbols?.length ? "?symbols=" + encodeURIComponent(symbols.join(",")) : "";
  return request<MarketFeedResponse>("/market" + suffix, { cache: "no-store" });
}

export async function getCryptoMarketFeed(mints?: string[]): Promise<MarketFeedResponse> {
  const suffix = mints?.length ? "?mints=" + encodeURIComponent(mints.join(",")) : "";
  return request<MarketFeedResponse>("/market/crypto" + suffix, { cache: "no-store" });
}

export async function getNews(symbol?: string, days = 7): Promise<NewsResponse> {
  const params = new URLSearchParams({ days: String(days) });
  if (symbol) params.set("symbol", symbol);
  return request<NewsResponse>("/news?" + params.toString(), { cache: "no-store" });
}

export async function getNewsFeed(days = 7): Promise<NewsResponse> {
  return request<NewsResponse>("/news/feed?days=" + encodeURIComponent(String(days)), { cache: "no-store" });
}

export async function createQuote(payload: QuoteRequest): Promise<QuoteResponse> {
  return request<QuoteResponse>("/quotes", { method: "POST", body: JSON.stringify(payload) });
}

function idempotencyKey(): string {
  return typeof crypto !== "undefined" && "randomUUID" in crypto
    ? crypto.randomUUID()
    : String(Date.now()) + "-" + Math.random().toString(36).slice(2);
}

function walletHeaders(wallet: string): HeadersInit {
  return { "X-Wallet-Address": wallet };
}

export async function getWatchlist(wallet: string): Promise<WatchlistResponse> {
  return request<WatchlistResponse>("/watchlist", {
    headers: walletHeaders(wallet),
    cache: "no-store",
  });
}

export async function addToWatchlist(mint: string, wallet: string, tab: DiscoveryTab = "stocks") {
  return request<WatchlistResponse["items"][number]>(
    "/watchlist/" + encodeURIComponent(mint) + "?tab=" + encodeURIComponent(tab),
    { method: "POST", headers: walletHeaders(wallet) },
  );
}

export async function removeFromWatchlist(mint: string, wallet: string): Promise<void> {
  await request<unknown>("/watchlist/" + encodeURIComponent(mint), {
    method: "DELETE",
    headers: walletHeaders(wallet),
  });
}

export async function createTrade(payload: TradeCreateRequest): Promise<TradeResponse> {
  return request<TradeResponse>("/trades", {
    method: "POST",
    headers: { ...walletHeaders(payload.wallet), "Idempotency-Key": idempotencyKey() },
    body: JSON.stringify(payload),
  });
}

export async function submitTrade(id: string, wallet: string, signature: string): Promise<TradeResponse> {
  return request<TradeResponse>("/trades/" + id + "/submit", {
    method: "POST",
    headers: walletHeaders(wallet),
    body: JSON.stringify({ wallet, signature }),
  });
}

export async function createOrder(payload: OrderCreateRequest): Promise<OrderResponse> {
  return request<OrderResponse>("/orders", {
    method: "POST",
    headers: { ...walletHeaders(payload.wallet), "Idempotency-Key": idempotencyKey() },
    body: JSON.stringify(payload),
  });
}

export async function submitOrder(id: string, wallet: string, signature: string): Promise<OrderResponse> {
  return request<OrderResponse>("/orders/" + id + "/submit", {
    method: "POST",
    headers: walletHeaders(wallet),
    body: JSON.stringify({ wallet, signature }),
  });
}

export async function getPortfolio(wallet: string): Promise<PortfolioResponse> {
  return request<PortfolioResponse>("/portfolio", {
    headers: walletHeaders(wallet),
    cache: "no-store",
  });
}

export async function createGift(payload: GiftCreateRequest): Promise<GiftResponse> {
  return request<GiftResponse>("/gifts", {
    method: "POST",
    headers: { ...walletHeaders(payload.sender_wallet), "Idempotency-Key": idempotencyKey() },
    body: JSON.stringify(payload),
  });
}

export async function getGift(claimCode: string): Promise<GiftResponse> {
  return request<GiftResponse>("/gifts/" + encodeURIComponent(claimCode), { cache: "no-store" });
}

export function apiErrorMessage(error: unknown): string {
  if (error instanceof ApiError) {
    try {
      const payload = JSON.parse(error.message) as { error?: { message?: string } };
      return payload.error?.message ?? "The API request failed.";
    } catch {
      return error.message || "The API request failed.";
    }
  }
  return error instanceof Error ? error.message : "The API request failed.";
}

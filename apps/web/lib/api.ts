import { API_URL } from "@/lib/constants";
import type { Asset, AssetListResponse } from "@/types";

export class ApiError extends Error {
  constructor(public readonly status: number, message: string) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { ...init, headers: { "Content-Type": "application/json", ...init?.headers } });
  if (!response.ok) throw new ApiError(response.status, await response.text());
  return response.json() as Promise<T>;
}

export async function getAssets(query?: string): Promise<Asset[]> {
  const suffix = query ? `?query=${encodeURIComponent(query)}` : "";
  const result = await request<AssetListResponse>(`/assets${suffix}`);
  return result.items;
}

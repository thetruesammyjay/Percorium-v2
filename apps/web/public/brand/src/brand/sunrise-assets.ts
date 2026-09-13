export type SunriseAssetType = "stock" | "etf" | "sector" | "index";

export interface SunriseAsset {
  mint: string;
  ticker: string;
  name: string;
  type: SunriseAssetType;
  mark: {
    kind: "custom" | "monogram";
    src?: string;
    initials?: string;
    background?: string;
    foreground?: string;
  };
  sunrise: {
    tradable: boolean;
    verified: boolean;
  };
}

/**
 * Populate this map with the canonical Sunrise mint addresses.
 * Do not infer mint addresses from ticker symbols.
 */
export const sunriseAssets: Record<string, SunriseAsset> = {};

/**
 * Example only — replace <MINT_ADDRESS> with Sunrise's canonical mint.
 *
 * sunriseAssets["<MINT_ADDRESS>"] = {
 *   mint: "<MINT_ADDRESS>",
 *   ticker: "AAPL",
 *   name: "Apple Inc.",
 *   type: "stock",
 *   mark: {
 *     kind: "monogram",
 *     src: "/brand/assets/generated/AAPL.svg",
 *     initials: "AAPL",
 *     background: "#4da2ff",
 *     foreground: "#ffffff",
 *   },
 *   sunrise: { tradable: true, verified: true },
 * };
 */

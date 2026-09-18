import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  outputFileTracingRoot: process.cwd(),
  webpack(config) {
    config.resolve ??= {};
    config.resolve.alias = {
      ...(config.resolve.alias ?? {}),
      // Privy dynamically loads this only inside a Farcaster mini app.
      // Percorium does not ship that integration, so keep the optional branch
      // out of the browser bundle and avoid a missing peer warning.
      "@farcaster/mini-app-solana": false,
    };
    return config;
  },
};

export default nextConfig;

import type { Metadata } from "next";

import { AppShell } from "@/components/layout/AppShell";
import { Providers } from "@/components/providers/Providers";
import { brandAssets } from "@/lib/brand";
import "./globals.css";

export const metadata: Metadata = {
  title: "Percorium — Tokenized stocks on Solana",
  description: "Discover, trade, and share official stock and ETF tokens.",
  icons: {
    icon: brandAssets.logo.favicon,
    shortcut: brandAssets.logo.favicon,
    apple: brandAssets.logo.favicon,
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>
        <Providers><AppShell>{children}</AppShell></Providers>
      </body>
    </html>
  );
}

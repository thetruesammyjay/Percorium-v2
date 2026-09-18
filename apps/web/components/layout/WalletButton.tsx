"use client";

import dynamic from "next/dynamic";
import { useCallback, useEffect, useState } from "react";

import { PRIVY_ENABLED } from "@/lib/constants";

function WalletButtonUnavailable() {
  return (
    <button className="wallet-button" type="button" disabled title="Add NEXT_PUBLIC_PRIVY_APP_ID to enable wallet login">
      <span className="wallet-dot" aria-hidden="true" />
      Wallet setup required
    </button>
  );
}

function WalletButtonLoading() {
  return (
    <button className="wallet-button" type="button" disabled aria-busy="true">
      <span className="wallet-dot" aria-hidden="true" />
      Connect wallet
    </button>
  );
}

const PrivyWalletIsland = dynamic(
  () => import("@/components/layout/PrivyWalletIsland").then((module) => module.PrivyWalletIsland),
  { ssr: false, loading: WalletButtonLoading },
);

export function WalletButton() {
  const [runtimeRequested, setRuntimeRequested] = useState(false);
  const [pendingIntent, setPendingIntent] = useState<"connect" | null>(null);

  const requestRuntime = useCallback((intent: "connect" | null = null) => {
    setRuntimeRequested(true);
    if (intent) setPendingIntent(intent);
  }, []);

  useEffect(() => {
    if (!PRIVY_ENABLED) return;
    const timer = window.setTimeout(() => requestRuntime(), 1200);
    return () => window.clearTimeout(timer);
  }, [requestRuntime]);

  if (!PRIVY_ENABLED) return <WalletButtonUnavailable />;
  if (runtimeRequested) {
    return <PrivyWalletIsland pendingIntent={pendingIntent} onIntentHandled={() => setPendingIntent(null)} />;
  }

  return (
    <button
      className="wallet-button"
      type="button"
      onPointerEnter={() => requestRuntime()}
      onFocus={() => requestRuntime()}
      onClick={() => requestRuntime("connect")}
    >
      <span className="wallet-dot" aria-hidden="true" />
      Connect wallet
    </button>
  );
}

"use client";

import { PrivyProvider, usePrivy } from "@privy-io/react-auth";
import { toSolanaWalletConnectors, useWallets as useSolanaWallets } from "@privy-io/react-auth/solana";
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { PRIVY_ENABLED, SOLANA_CLUSTER } from "@/lib/constants";

type WalletContextValue = {
  connected: boolean;
  address?: string;
  setupRequired: boolean;
  signAndSend?: (transaction: Uint8Array) => Promise<Uint8Array>;
};

type WalletRuntime = WalletContextValue & {
  setRuntime: (value: Omit<WalletContextValue, "setupRequired">) => void;
};

const WalletContext = createContext<WalletContextValue>({
  connected: false,
  setupRequired: !PRIVY_ENABLED,
});

const WalletRuntimeContext = createContext<WalletRuntime | null>(null);

export function useWallet() {
  return useContext(WalletContext);
}

function WalletProvider({ children }: Readonly<{ children: React.ReactNode }>) {
  const [runtime, setRuntimeState] = useState<Omit<WalletContextValue, "setupRequired">>({ connected: false });
  const setRuntime = useCallback((value: Omit<WalletContextValue, "setupRequired">) => {
    setRuntimeState(value);
  }, []);
  const value = useMemo(() => ({ ...runtime, setupRequired: !PRIVY_ENABLED }), [runtime]);
  const runtimeValue = useMemo(() => ({ ...value, setRuntime }), [value, setRuntime]);

  return (
    <WalletRuntimeContext.Provider value={runtimeValue}>
      <WalletContext.Provider value={value}>{children}</WalletContext.Provider>
    </WalletRuntimeContext.Provider>
  );
}

function PrivyWalletBridge({ children }: Readonly<{ children: React.ReactNode }>) {
  const { authenticated } = usePrivy();
  const { wallets } = useSolanaWallets();
  const runtime = useContext(WalletRuntimeContext);
  const wallet = wallets[0];
  const setRuntime = runtime?.setRuntime;
  const solanaChain = (SOLANA_CLUSTER === "mainnet-beta" ? "solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp" : SOLANA_CLUSTER === "testnet" ? "solana:4uhcVJyU9pJkvQyS88uRDiswHXSCkY3z" : "solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1") as `${string}:${string}`;

  useEffect(() => {
    if (!setRuntime) return;
    const connected = Boolean(authenticated && wallet);
    setRuntime({
      connected,
      address: connected ? wallet.address : undefined,
      signAndSend: connected
        ? async (transaction: Uint8Array) => {
            const response = await wallet.signAndSendTransaction({ transaction, chain: solanaChain });
            return response.signature;
          }
        : undefined,
    });
  }, [authenticated, setRuntime, solanaChain, wallet]);

  return <>{children}</>;
}

const solanaConnectors = toSolanaWalletConnectors({ shouldAutoConnect: false });

export function Providers({ children }: Readonly<{ children: React.ReactNode }>) {
  if (!PRIVY_ENABLED) return <WalletProvider>{children}</WalletProvider>;

  return (
    <PrivyProvider
      appId={process.env.NEXT_PUBLIC_PRIVY_APP_ID ?? ""}
      config={{
        appearance: {
          theme: "light",
          accentColor: "#000000",
          walletChainType: "solana-only",
        },
        loginMethods: ["google", "wallet"],
        externalWallets: {
          solana: { connectors: solanaConnectors },
        },
        embeddedWallets: { solana: { createOnLogin: "all-users" } },
      }}
    >
      <WalletProvider>
        <PrivyWalletBridge>{children}</PrivyWalletBridge>
      </WalletProvider>
    </PrivyProvider>
  );
}
"use client";

import { createContext, useCallback, useContext, useMemo, useState } from "react";

import { PRIVY_ENABLED } from "@/lib/constants";

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

export function useWalletRuntime() {
  const runtime = useContext(WalletRuntimeContext);
  if (!runtime) {
    throw new Error("useWalletRuntime must be used inside WalletProvider");
  }
  return runtime;
}

export function Providers({ children }: Readonly<{ children: React.ReactNode }>) {
  return <WalletProvider>{children}</WalletProvider>;
}

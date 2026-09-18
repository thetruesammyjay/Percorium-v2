"use client";

import { PrivyProvider, useConnectWallet, usePrivy } from "@privy-io/react-auth";
import { toSolanaWalletConnectors, useWallets as useSolanaWallets } from "@privy-io/react-auth/solana";
import { useEffect } from "react";

import { useWallet, useWalletRuntime } from "@/components/providers/Providers";
import { SOLANA_CLUSTER } from "@/lib/constants";
import { shortenAddress } from "@/lib/utils";

type Props = {
  pendingIntent: "connect" | null;
  onIntentHandled: () => void;
};

function PrivyWalletBridge({ children }: Readonly<{ children: React.ReactNode }>) {
  const { authenticated } = usePrivy();
  const { wallets } = useSolanaWallets();
  const { setRuntime } = useWalletRuntime();
  const wallet = wallets[0];
  const solanaChain = (SOLANA_CLUSTER === "mainnet-beta" ? "solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp" : SOLANA_CLUSTER === "testnet" ? "solana:4uhcVJyU9pJkvQyS88uRDiswHXSCkY3z" : "solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1") as `${string}:${string}`;

  useEffect(() => {
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

function PrivyWalletButton({ pendingIntent, onIntentHandled }: Props) {
  const { ready, authenticated, login, logout } = usePrivy();
  const { connectWallet } = useConnectWallet();
  const wallet = useWallet();

  useEffect(() => {
    if (pendingIntent !== "connect" || !ready) return;
    onIntentHandled();
    if (wallet.connected && authenticated) return;
    if (authenticated) {
      connectWallet();
    } else {
      login();
    }
  }, [authenticated, connectWallet, login, onIntentHandled, pendingIntent, ready, wallet.connected]);

  const handleClick = () => {
    if (!ready) return;
    if (wallet.connected && authenticated) {
      void logout();
      return;
    }
    if (authenticated) {
      connectWallet();
      return;
    }
    login();
  };

  const label = !ready
    ? "Loading wallet"
    : wallet.connected && wallet.address
      ? shortenAddress(wallet.address)
      : authenticated
        ? "Choose wallet"
        : "Connect wallet";

  return (
    <button className={"wallet-button" + (wallet.connected ? " wallet-connected" : "")} type="button" onClick={handleClick} disabled={!ready}>
      <span className="wallet-dot" aria-hidden="true" />
      {label}
    </button>
  );
}

const solanaConnectors = toSolanaWalletConnectors({ shouldAutoConnect: false });

export function PrivyWalletIsland({ pendingIntent, onIntentHandled }: Props) {
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
      <PrivyWalletBridge>
        <PrivyWalletButton pendingIntent={pendingIntent} onIntentHandled={onIntentHandled} />
      </PrivyWalletBridge>
    </PrivyProvider>
  );
}

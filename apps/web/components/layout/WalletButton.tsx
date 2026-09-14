"use client";

import { useConnectWallet, usePrivy } from "@privy-io/react-auth";

import { PRIVY_ENABLED } from "@/lib/constants";
import { shortenAddress } from "@/lib/utils";
import { useWallet } from "@/components/providers/Providers";

function WalletButtonUnavailable() {
  return (
    <button className="wallet-button" type="button" disabled title="Add NEXT_PUBLIC_PRIVY_APP_ID to enable wallet login">
      <span className="wallet-dot" aria-hidden="true" />
      Wallet setup required
    </button>
  );
}

function PrivyWalletButton() {
  const { ready, authenticated, login, logout } = usePrivy();
  const { connectWallet } = useConnectWallet();
  const wallet = useWallet();

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

export function WalletButton() {
  return PRIVY_ENABLED ? <PrivyWalletButton /> : <WalletButtonUnavailable />;
}
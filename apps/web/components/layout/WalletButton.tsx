"use client";

import { useState } from "react";

export function WalletButton() {
  const [connected, setConnected] = useState(false);
  return <button className={`wallet-button${connected ? " wallet-connected" : ""}`} onClick={() => setConnected((value) => !value)}><span className="wallet-dot" aria-hidden="true" />{connected ? "Wallet connected" : "Connect wallet"}</button>;
}
